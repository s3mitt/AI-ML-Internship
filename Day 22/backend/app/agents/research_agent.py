"""Research Agent Implementation.

Role:
- Performs research and information gathering.
- Identifies relevant evidence, facts, empirical data, and primary sources.
- Produces structured findings and catalogs references in Shared State.
"""

from __future__ import annotations
import logging
from typing import Optional

from .base_agent import BaseAgent
from ..services.llm_service import get_llm_service
from ..state.research_state import Finding, ResearchState, SourceReference

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Gathers raw empirical evidence and sources related to the topic."""

    def __init__(self):
        super().__init__(
            name="Research Agent",
            role="Information Gathering, Primary Fact Extraction, and Source Cataloging",
        )
        self.llm_service = get_llm_service()

    async def _process(self, state: ResearchState) -> ResearchState:
        is_refinement = state.refinement_iterations > 0
        refinement_instructions: Optional[str] = None

        if is_refinement and state.critique:
            issues = state.critique.get("identified_issues", [])
            recs = state.critique.get("recommendations", [])
            refinement_instructions = f"Issues: {'; '.join(issues)}. Recommendations: {'; '.join(recs)}"

        raw_data = await self.llm_service.generate_research(
            query=state.query,
            preferences=state.preferences,
            is_refinement=is_refinement,
            refinement_instructions=refinement_instructions,
        )

        # Parse findings into typed Finding models
        existing_finding_ids = {f.id for f in state.research_findings}
        for item in raw_data.get("findings", []):
            finding_id = item.get("id")
            if not finding_id or finding_id not in existing_finding_ids:
                finding = Finding(
                    id=item.get("id") or f"fnd_{len(state.research_findings) + 1:02d}",
                    title=item.get("title", "Research Finding"),
                    fact=item.get("fact", ""),
                    evidence=item.get("evidence", ""),
                    source_id=item.get("source_id", "src_01"),
                    confidence=float(item.get("confidence", 0.9)),
                    domain=item.get("domain", "General"),
                )
                state.research_findings.append(finding)

        # Parse sources into typed SourceReference models
        existing_source_ids = {s.id for s in state.sources}
        for item in raw_data.get("sources", []):
            src_id = item.get("id")
            if not src_id or src_id not in existing_source_ids:
                source = SourceReference(
                    id=item.get("id") or f"src_{len(state.sources) + 1:02d}",
                    title=item.get("title", "Source Citation"),
                    url_or_doi=item.get("url_or_doi", "https://doi.org/reference"),
                    publication_year=item.get("publication_year", 2024),
                    author_or_org=item.get("author_or_org", "Academic/Industry Organization"),
                    relevance_summary=item.get("relevance_summary", "Core contextual evidence."),
                )
                state.sources.append(source)

        state.research_notes = raw_data.get("notes", f"Investigated query: {state.query}")
        return state

    def _summarize_input(self, state: ResearchState) -> str:
        refine_str = f" (Refinement #{state.refinement_iterations})" if state.refinement_iterations > 0 else ""
        return f"Query: '{state.query}'{refine_str}"

    def _summarize_output(self, state: ResearchState) -> str:
        return f"Compiled {len(state.research_findings)} findings across {len(state.sources)} peer/industry sources."
