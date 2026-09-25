"""Writer Agent Implementation.

Role:
- Converts validated research findings, analysis, and critic feedback into a publication-grade report.
- Incorporates recommendations from the Critic.
- Produces clean Markdown with executive sections, citations, and strategic recommendations.
- Stores the report into Shared State.
"""

from __future__ import annotations
from datetime import datetime, timezone
import logging
from typing import Any, Dict

from .base_agent import BaseAgent
from ..services.llm_service import get_llm_service
from ..state.research_state import ResearchState

logger = logging.getLogger(__name__)


class Writer(BaseAgent):
    """Synthesizes all preceding agent outputs into an executive research document."""

    def __init__(self):
        super().__init__(
            name="Writer",
            role="Document Synthesis, Citation Linking, and Critic Feedback Integration",
        )
        self.llm_service = get_llm_service()

    async def _process(self, state: ResearchState) -> ResearchState:
        if not state.research_findings:
            raise ValueError("Writer cannot proceed: Research findings missing from Shared State.")
        if not state.analysis:
            raise ValueError("Writer cannot proceed: Analysis missing from Shared State.")
        if not state.critique:
            raise ValueError("Writer cannot proceed: Critique missing from Shared State.")

        findings_dicts = [f.model_dump() for f in state.research_findings]
        sources_dicts = [s.model_dump() for s in state.sources]

        report_md = await self.llm_service.generate_report(
            query=state.query,
            findings=findings_dicts,
            sources=sources_dicts,
            analysis=state.analysis,
            critique=state.critique,
        )

        state.final_report = report_md
        state.report_metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "character_count": len(report_md),
            "word_count": len(report_md.split()),
            "sources_cited": len(sources_dicts),
            "findings_referenced": len(findings_dicts),
            "critic_score": state.critique.get("quality_score", 0.0),
        }

        return state

    def _summarize_input(self, state: ResearchState) -> str:
        score = state.critique.get("quality_score", "N/A")
        return (
            f"Drafting report from {len(state.research_findings)} findings, "
            f"{len(state.sources)} sources, and Critic feedback (score {score})."
        )

    def _summarize_output(self, state: ResearchState) -> str:
        words = state.report_metadata.get("word_count", 0)
        return f"Compiled executive report of {words} words with citations and recommendations."
