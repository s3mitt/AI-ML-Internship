"""Critic Agent Implementation.

Role:
- Reviews gathered research findings and thematic analysis.
- Detects unsupported claims, logical leaps, and missing perspectives.
- Evaluates bias, consistency, and empirical validity.
- Assigns a quantitative quality score (0.0 to 10.0).
- Suggests concrete improvements.
- Signals refinement if quality criteria are unmet.
"""

from __future__ import annotations
import logging
from typing import Any, Dict

from .base_agent import BaseAgent
from ..services.llm_service import get_llm_service
from ..state.research_state import ResearchState

logger = logging.getLogger(__name__)


class Critic(BaseAgent):
    """Conducts peer review and validation of research findings and analysis."""

    def __init__(self, quality_threshold: float = 7.5):
        super().__init__(
            name="Critic",
            role="Peer Review, Quality Scoring, Bias Detection, and Refinement Recommendation",
        )
        self.quality_threshold = quality_threshold
        self.llm_service = get_llm_service()

    async def _process(self, state: ResearchState) -> ResearchState:
        if not state.research_findings:
            raise ValueError("Critic cannot proceed: Research findings missing from Shared State.")
        if not state.analysis:
            raise ValueError("Critic cannot proceed: Analysis missing from Shared State.")

        findings_dicts = [f.model_dump() for f in state.research_findings]

        critique_result = await self.llm_service.generate_critique(
            query=state.query,
            findings=findings_dicts,
            analysis=state.analysis,
            iteration=state.refinement_iterations + 1,
        )

        # Enforce quality scoring logic
        score = float(critique_result.get("quality_score", 8.0))
        passes = score >= self.quality_threshold
        critique_result["passes_validation"] = passes

        # If user explicitly requested refinement test or score is low, flag refinement
        # Note: Avoid infinite loop by checking state.refinement_iterations < state.max_refinements
        if not passes and state.refinement_iterations < state.max_refinements:
            critique_result["needs_refinement"] = True
            if not critique_result.get("target_refinement_stage"):
                critique_result["target_refinement_stage"] = "research"
        else:
            critique_result["needs_refinement"] = False

        state.critique = critique_result
        return state

    def _summarize_input(self, state: ResearchState) -> str:
        themes_cnt = len(state.analysis.get("themes", []))
        return f"Evaluating {len(state.research_findings)} findings across {themes_cnt} themes."

    def _summarize_output(self, state: ResearchState) -> str:
        score = state.critique.get("quality_score", 0.0)
        passes = state.critique.get("passes_validation", False)
        needs_ref = state.critique.get("needs_refinement", False)
        status_label = "Approved" if passes else ("Refinement Required" if needs_ref else "Marginal Pass")
        return f"Assigned Score: {score}/10.0 ({status_label}). Issues flagged: {len(state.critique.get('identified_issues', []))}."
