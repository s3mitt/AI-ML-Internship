"""Unit tests for the Research Agent."""

import pytest
from backend.app.agents.research_agent import ResearchAgent
from backend.app.state.research_state import ResearchState


@pytest.mark.asyncio
async def test_research_agent_execution():
    """Verify that ResearchAgent extracts empirical findings, sources, and logs history."""
    agent = ResearchAgent()
    state = ResearchState(query="Impact of generative AI on software development")

    updated_state = await agent.execute(state, step_index=1)

    assert len(updated_state.research_findings) > 0
    assert len(updated_state.sources) > 0
    assert updated_state.research_notes != ""

    # Verify first finding structure
    first_finding = updated_state.research_findings[0]
    assert first_finding.title != ""
    assert first_finding.fact != ""
    assert first_finding.evidence != ""
    assert first_finding.confidence > 0.0
    assert first_finding.source_id.startswith("src_")

    # Verify execution history logging
    assert len(updated_state.agent_history) == 1
    record = updated_state.agent_history[0]
    assert record.agent == "Research Agent"
    assert record.status == "completed"
    assert record.step_index == 1
    assert "findings" in record.output_summary.lower()


@pytest.mark.asyncio
async def test_research_agent_refinement():
    """Verify that ResearchAgent handles critic-directed refinement requests."""
    agent = ResearchAgent()
    state = ResearchState(query="Impact of generative AI on software development")
    state = await agent.execute(state, step_index=1)
    initial_findings_count = len(state.research_findings)

    # Simulate Critic feedback requiring refinement
    state.refinement_iterations = 1
    state.critique = {
        "identified_issues": ["Need more empirical benchmark data."],
        "recommendations": ["Incorporate 2024 peer-reviewed metrics."],
    }

    state = await agent.execute(state, step_index=2)
    assert len(state.research_findings) >= initial_findings_count
    assert len(state.agent_history) == 2
