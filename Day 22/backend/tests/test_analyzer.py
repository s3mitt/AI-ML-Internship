"""Unit tests for the Analyzer agent."""

import pytest
from backend.app.agents.research_agent import ResearchAgent
from backend.app.agents.analyzer import Analyzer
from backend.app.state.research_state import ResearchState


@pytest.mark.asyncio
async def test_analyzer_empty_state_guardrail():
    """Verify that Analyzer raises ValueError if research findings are absent."""
    analyzer = Analyzer()
    empty_state = ResearchState(query="Quantum Computing")

    with pytest.raises(ValueError, match="No research findings present"):
        await analyzer.execute(empty_state, step_index=2)

    assert len(empty_state.errors) == 1
    assert empty_state.errors[0]["agent"] == "Analyzer"


@pytest.mark.asyncio
async def test_analyzer_synthesizes_themes_and_facts():
    """Verify that Analyzer synthesizes themes, separates facts vs assumptions, and updates state."""
    researcher = ResearchAgent()
    analyzer = Analyzer()

    state = ResearchState(query="Impact of generative AI on software development")
    state = await researcher.execute(state, step_index=1)

    state = await analyzer.execute(state, step_index=2)

    assert bool(state.analysis) is True
    assert "themes" in state.analysis
    assert len(state.analysis["themes"]) > 0

    # Verify theme structure
    theme = state.analysis["themes"][0]
    assert "name" in theme
    assert "summary" in theme
    assert "impact_level" in theme

    # Verify fact vs assumptions separation
    assert "fact_vs_assumptions" in state.analysis
    facts = state.analysis["fact_vs_assumptions"].get("verified_facts", [])
    assumptions = state.analysis["fact_vs_assumptions"].get("unverified_assumptions", [])
    assert len(facts) > 0
    assert len(assumptions) > 0

    # Verify history entry
    assert len(state.agent_history) == 2
    record = state.agent_history[1]
    assert record.agent == "Analyzer"
    assert record.status == "completed"
    assert record.step_index == 2
