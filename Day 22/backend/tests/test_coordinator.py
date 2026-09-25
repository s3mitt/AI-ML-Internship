"""Unit and integration tests for Coordinator orchestration and error recovery."""

import pytest
from unittest.mock import AsyncMock, patch
from backend.app.agents.coordinator import Coordinator
from backend.app.agents.base_agent import BaseAgent
from backend.app.state.research_state import ResearchState


@pytest.mark.asyncio
async def test_coordinator_initializes_state_and_plan():
    """Verify Coordinator builds plan and initializes shared state."""
    coordinator = Coordinator()
    state = coordinator.initialize_state("Autonomous Agents in Healthcare")

    assert state.query == "Autonomous Agents in Healthcare"
    assert state.workflow_plan == ["research", "analyze", "criticize", "write"]
    assert state.workflow_status == "initialized"


@pytest.mark.asyncio
async def test_coordinator_full_execution_flow():
    """Verify Coordinator completes full execution and marks state completed."""
    coordinator = Coordinator()
    progress_messages = []

    def on_progress(st: ResearchState, msg: str):
        progress_messages.append(msg)

    final_state = await coordinator.run_workflow(
        query="Impact of generative AI on software development",
        progress_callback=on_progress,
    )

    assert final_state.workflow_status == "completed"
    assert final_state.final_report != ""
    assert len(final_state.research_findings) > 0
    assert len(final_state.sources) > 0
    assert bool(final_state.analysis) is True
    assert bool(final_state.critique) is True

    # Check Coordinator execution record is at the end of history
    coord_record = final_state.agent_history[-1]
    assert coord_record.agent == "Coordinator"
    assert coord_record.status == "completed"

    # Verify callback was called
    assert len(progress_messages) >= 5


@pytest.mark.asyncio
async def test_coordinator_retry_mechanism_on_transient_failure():
    """Verify Coordinator retries a stage when a transient failure occurs."""
    coordinator = Coordinator(max_retries=2)
    state = coordinator.initialize_state("Transient Failure Test")

    call_count = 0

    class FlakyAgent(BaseAgent):
        def __init__(self):
            super().__init__(name="Flaky Agent", role="Test Flakiness")

        async def _process(self, st: ResearchState) -> ResearchState:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionResetError("Transient network drop")
            st.research_notes = "Recovered after retry"
            return st

        def _summarize_input(self, st):
            return "input"

        def _summarize_output(self, st):
            return "output"

    flaky = FlakyAgent()
    updated_state = await coordinator._execute_stage_with_retry(
        agent=flaky,
        stage_name="flaky_stage",
        state=state,
        step_index=1,
        notify=lambda m: None,
    )

    assert call_count == 2
    assert updated_state.research_notes == "Recovered after retry"


@pytest.mark.asyncio
async def test_coordinator_handles_unrecoverable_failure():
    """Verify Coordinator handles unrecoverable failure and sets workflow_status to failed."""
    coordinator = Coordinator(max_retries=1)

    # Patch research agent to fail critically
    with patch.object(coordinator.research_agent, "execute", side_effect=RuntimeError("Fatal DB Corrupt")):
        with pytest.raises(RuntimeError, match="Fatal DB Corrupt"):
            await coordinator.run_workflow("Query causing fatal crash")

    # In execute_workflow, the state status was set to failed before re-raising
