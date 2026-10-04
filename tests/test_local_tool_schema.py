import asyncio
import threading

from anytool.grounding.core.tool.local_tool import LocalTool


class SyncEcho(LocalTool):
    def _run(self, text: str, count: int = 1):
        assert threading.current_thread() is not threading.main_thread()
        return text * count


class AsyncEcho(LocalTool):
    async def _arun(self, text: str):
        assert threading.current_thread() is threading.main_thread()
        return text


def test_sync_local_tool_advertises_and_accepts_its_parameters():
    tool = SyncEcho()
    assert tool.schema.parameters["required"] == ["text"]
    assert tool.schema.parameters["properties"]["count"]["default"] == 1
    result = asyncio.run(tool.arun(text="hello", count=2))
    assert result.is_success
    assert result.content == "hellohello"
    assert asyncio.run(tool.arun()).is_error


def test_async_local_tool_keeps_its_own_signature_and_dispatch():
    tool = AsyncEcho()
    assert tool.schema.parameters["required"] == ["text"]
    result = asyncio.run(tool.arun(text="hello"))
    assert result.is_success
    assert result.content == "hello"
