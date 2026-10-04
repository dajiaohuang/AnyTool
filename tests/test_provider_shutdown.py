import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest

from anytool.grounding.core.grounding_client import GroundingClient


def test_shutdown_closes_provider_sessions_not_registered_with_client():
    client = GroundingClient.__new__(GroundingClient)
    client._sessions = {}
    provider = SimpleNamespace(close_all_sessions=AsyncMock())
    client._registry = SimpleNamespace(list=lambda: {"test": provider})
    asyncio.run(client.close_all_sessions())
    provider.close_all_sessions.assert_awaited_once()


def test_shutdown_attempts_other_providers_after_a_close_failure():
    client = GroundingClient.__new__(GroundingClient)
    client._sessions = {"broken": object()}
    client.close_session = AsyncMock(side_effect=ValueError("close failed"))
    first = SimpleNamespace(close_all_sessions=AsyncMock(side_effect=ValueError("provider failed")))
    second = SimpleNamespace(close_all_sessions=AsyncMock())
    client._registry = SimpleNamespace(list=lambda: {"first": first, "second": second})
    with pytest.raises(ValueError, match="close failed"):
        asyncio.run(client.close_all_sessions())
    first.close_all_sessions.assert_awaited_once()
    second.close_all_sessions.assert_awaited_once()
