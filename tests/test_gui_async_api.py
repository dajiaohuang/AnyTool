import asyncio

import pytest
from anthropic import AsyncAnthropic
from anthropic import _client
import httpx

# Match the HTTP package used by the installed SDK, including pre-1.x releases.
httpx = getattr(_client, "httpx2", httpx)

from anytool.grounding.backends.gui import anthropic_client


@pytest.mark.parametrize("retry", [False, True])
def test_gui_planning_uses_async_requests_and_closes_client(monkeypatch, retry):
    async def run():
        calls = 0
        ticked = False

        async def handler(request):
            nonlocal calls
            calls += 1
            await asyncio.sleep(0.05)
            assert ticked
            if retry and calls == 1:
                return httpx.Response(400, json={"type": "error", "error": {"type": "invalid_request_error", "message": "retry test"}})
            return httpx.Response(200, json={"id": "message", "type": "message", "role": "assistant", "model": "claude-sonnet-4-5", "content": [{"type": "text", "text": "Finished"}], "stop_reason": "end_turn", "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1}})

        transport = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        sdk = AsyncAnthropic(api_key="test", http_client=transport, max_retries=0)
        client = anthropic_client.AnthropicGUIClient(api_key="test", enable_prompt_caching=False)
        monkeypatch.setattr(client, "_create_client", lambda *args: sdk)
        monkeypatch.setattr(client, "_resize_screenshot", lambda data: data)
        monkeypatch.setattr(anthropic_client, "API_RETRY_TIMES", 2)
        monkeypatch.setattr(anthropic_client, "API_RETRY_INTERVAL", 0.05)

        async def tick():
            nonlocal ticked
            await asyncio.sleep(0.01)
            ticked = True

        result, _ = await asyncio.gather(client.plan_action("test", b"image"), tick())
        assert result == ("Finished", [])
        assert calls == (2 if retry else 1)
        assert transport.is_closed

    asyncio.run(run())


def test_cancelled_gui_request_closes_async_client(monkeypatch):
    async def run():
        started = asyncio.Event()

        async def handler(request):
            started.set()
            await asyncio.Event().wait()

        transport = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        sdk = AsyncAnthropic(api_key="test", http_client=transport, max_retries=0)
        client = anthropic_client.AnthropicGUIClient(api_key="test", enable_prompt_caching=False)
        monkeypatch.setattr(client, "_create_client", lambda *args: sdk)
        monkeypatch.setattr(client, "_resize_screenshot", lambda data: data)
        task = asyncio.create_task(client.plan_action("test", b"image"))
        await asyncio.wait_for(started.wait(), 2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert transport.is_closed

    asyncio.run(run())
