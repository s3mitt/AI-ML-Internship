"""Unit tests for the Critic agent."""

import pytest
from backend.app.agents.research_agent import ResearchAgent
from backend.app.agents.analyzer import Analyzer
from backend.app.agents.critic import Critic
from backend.app.state.research_state import ResearchState


@pytest.mark.asyncio
async def test_critic_requires_findings_and_analysis():
    """Verify that Critic refuses execution if prerequisites are missing."""
    critic = Critic()
    state = ResearchState(query="Test query")

    with pytest.raises(ValueError, match="Research findings missing"):
        await critic.execute(state, step_index=3)


@pytest.mark.asyncio
async def test_critic_produces_quality_score_and_critique():
    """Verify that Critic computes quality scores, issues, recommendations, and bias assessment."""
    researcher = ResearchAgent()
    analyzer = Analyzer()
    critic = Critic(quality_threshold=7.5)

    state = ResearchState(query="Impact of generative AI on software development")
    state = await researcher.execute(state, step_index=1)
    state = await analyzer.execute(state, step_index=2)
    state = await critic.execute(state, step_index=3)

    assert bool(state.critique) is True
    assert "quality_score" in state.critique
    assert 0.0 <= state.critique["quality_score"] <= 10.0
    assert "passes_validation" in state.critique
    assert isinstance(state.critique["identified_issues"], list)
    assert isinstance(state.critique["recommendations"], list)
    assert "bias_assessment" in state.critique

    # Verify history
    record = state.agent_history[-1]
    assert record.agent == "Critic"
    assert record.status == "completed"


@pytest.mark.asyncio
async def test_critic_refinement_trigger_when_threshold_unmet():
    """Verify Critic flags needs_refinement when quality score is below threshold."""
    critic = Critic(quality_threshold=9.5)  # Set artificially high threshold to trigger refinement

    state = ResearchState(query="Impact of generative AI on software development")
    researcher = ResearchAgent()
    analyzer = Analyzer()
    state = await researcher.execute(state, step_index=1)
    state = await analyzer.execute(state, step_index=2)

    state = await critic.execute(state, step_index=3)

    # Score of ~8.8 will fail threshold 9.5 and request refinement
    assert state.critique["passes_validation"] is False
    assert state.critique["needs_refinement"] is True
    assert state.critique["target_refinement_stage"] is not None
