"""Unit tests for the Writer agent."""

import pytest
from backend.app.agents.research_agent import ResearchAgent
from backend.app.agents.analyzer import Analyzer
from backend.app.agents.critic import Critic
from backend.app.agents.writer import Writer
from backend.app.state.research_state import ResearchState


@pytest.mark.asyncio
async def test_writer_guardrails():
    """Verify Writer requires research, analysis, and critique before generating report."""
    writer = Writer()
    state = ResearchState(query="Incomplete state query")

    with pytest.raises(ValueError, match="Research findings missing"):
        await writer.execute(state, step_index=4)


@pytest.mark.asyncio
async def test_writer_generates_markdown_report_with_metadata():
    """Verify Writer synthesizes an executive markdown document and records metadata."""
    researcher = ResearchAgent()
    analyzer = Analyzer()
    critic = Critic()
    writer = Writer()

    state = ResearchState(query="Impact of generative AI on software development")
    state = await researcher.execute(state, step_index=1)
    state = await analyzer.execute(state, step_index=2)
    state = await critic.execute(state, step_index=3)
    state = await writer.execute(state, step_index=4)

    assert state.final_report != ""
    assert "# Executive Research Report" in state.final_report
    assert "## 1. Executive Summary" in state.final_report
    assert "## 6. References & Verified Sources" in state.final_report

    # Check metadata
    assert "word_count" in state.report_metadata
    assert state.report_metadata["word_count"] > 100
    assert state.report_metadata["sources_cited"] > 0

    # Check history
    record = state.agent_history[-1]
    assert record.agent == "Writer"
    assert record.status == "completed"
