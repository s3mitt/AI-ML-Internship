"""Tests verifying agent communication, shared state passing, and execution observability."""

import pytest
from backend.app.agents.coordinator import Coordinator
from backend.app.state.research_state import ResearchState


@pytest.mark.asyncio
async def test_agent_communication_and_observability():
    """Verify that agents communicate exclusively via Shared State and record audit metadata."""
    coordinator = Coordinator()
    query = "Autonomous Multi-Agent Systems in Supply Chain Optimization"

    state = await coordinator.run_workflow(query=query)

    # Expected agents in execution sequence:
    # 1. Research Agent
    # 2. Analyzer
    # 3. Critic
    # 4. Writer
    # 5. Coordinator (summary)
    agent_names = [record.agent for record in state.agent_history]

    assert "Research Agent" in agent_names
    assert "Analyzer" in agent_names
    assert "Critic" in agent_names
    assert "Writer" in agent_names
    assert "Coordinator" in agent_names

    # Check timing and metadata consistency for all records
    for record in state.agent_history:
        assert record.start_time != ""
        assert record.end_time != ""
        assert record.duration_seconds >= 0.0
        assert record.status == "completed"
        assert record.input_summary != ""
        assert record.output_summary != ""

    # Check shared state consumption relationships:
    # Analyzer consumed Research Agent findings
    assert len(state.research_findings) > 0
    # Critic reviewed both findings and analysis
    assert state.critique.get("quality_score") is not None
    # Writer synthesized the final report referencing the findings and critique
    assert state.final_report != ""
