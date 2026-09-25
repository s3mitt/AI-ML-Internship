"""Analyzer Agent Implementation.

Role:
- Processes research findings from Shared State.
- Identifies key themes and categorizes evidence.
- Detects patterns, relationships, and contradictions.
- Separates verified facts from assumptions.
- Stores structured analysis in Shared State.
"""

from __future__ import annotations
import logging
from typing import Any, Dict

from .base_agent import BaseAgent
from ..services.llm_service import get_llm_service
from ..state.research_state import ResearchState

logger = logging.getLogger(__name__)


class Analyzer(BaseAgent):
    """Processes raw findings into structured themes, patterns, and insights."""

    def __init__(self):
        super().__init__(
            name="Analyzer",
            role="Thematic Synthesis, Pattern Recognition, Fact/Assumption Separation",
        )
        self.llm_service = get_llm_service()

    async def _process(self, state: ResearchState) -> ResearchState:
        if not state.research_findings:
            raise ValueError("Analyzer cannot proceed: No research findings present in Shared State.")

        # Extract findings and sources as clean serializable dicts
        findings_dicts = [f.model_dump() for f in state.research_findings]
        sources_dicts = [s.model_dump() for s in state.sources]

        analysis_result = await self.llm_service.generate_analysis(
            query=state.query,
            findings=findings_dicts,
            sources=sources_dicts,
        )

        # Store structured analysis directly in Shared State
        state.analysis = analysis_result
        return state

    def _summarize_input(self, state: ResearchState) -> str:
        return f"Ingested {len(state.research_findings)} findings and {len(state.sources)} sources from Shared State."

    def _summarize_output(self, state: ResearchState) -> str:
        themes = state.analysis.get("themes", [])
        facts = state.analysis.get("fact_vs_assumptions", {}).get("verified_facts", [])
        assumptions = state.analysis.get("fact_vs_assumptions", {}).get("unverified_assumptions", [])
        return (
            f"Synthesized {len(themes)} major themes, isolated {len(facts)} verified facts "
            f"and {len(assumptions)} unverified assumptions."
        )
