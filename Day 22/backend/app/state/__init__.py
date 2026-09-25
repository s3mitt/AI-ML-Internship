"""Shared State Package for Multi-Agent Workflow."""
from .research_state import (
    ResearchState,
    AgentExecutionRecord,
    Finding,
    SourceReference,
    AnalysisTheme,
    CriticEvaluation,
    FinalReportSection,
)

__all__ = [
    "ResearchState",
    "AgentExecutionRecord",
    "Finding",
    "SourceReference",
    "AnalysisTheme",
    "CriticEvaluation",
    "FinalReportSection",
]
