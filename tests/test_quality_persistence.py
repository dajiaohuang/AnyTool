import asyncio

from anytool.grounding.core.quality.manager import ToolQualityManager
from anytool.grounding.core.tool.base import BaseTool
from anytool.grounding.core.types import ToolResult


class SampleTool(BaseTool):
    async def _arun(self):
        return "done"


def test_explicit_save_preserves_execution_count_and_evolution_schedule(tmp_path):
    manager = ToolQualityManager(cache_dir=tmp_path, auto_save=False, evolve_interval=3)
    tool = SampleTool()

    async def run():
        for _ in range(2):
            await manager.record_execution(tool, ToolResult(status="success", content="done"), 1)
        await manager.save()

    asyncio.run(run())
    restored = ToolQualityManager(cache_dir=tmp_path, auto_save=False, evolve_interval=3)
    assert restored.get_record(tool).total_calls == 2
    assert restored._global_execution_count == 2
    assert not restored.should_evolve()
    asyncio.run(restored.record_execution(tool, ToolResult(status="success", content="done"), 1))
    assert restored.should_evolve()
