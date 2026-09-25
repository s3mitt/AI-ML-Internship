"""Pydantic API DTO models for request and response validation."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..state.research_state import AgentExecutionRecord, Finding, SourceReference


class ResearchRequest(BaseModel):
    """Payload for initiating a research workflow."""
    query: str = Field(
        ...,
        min_length=3,
        description="The research query, question, or topic to investigate.",
        examples=["Impact of generative AI on software development"],
    )
    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional research preferences (e.g., academic focus, time horizon, specific sub-domains).",
    )


class ResearchResponse(BaseModel):
    """Response returned upon completing or querying research workflow."""
    workflow_id: str
    status: str
    query: str
    final_report: str
    agent_history: List[AgentExecutionRecord]
    research_findings: List[Finding] = Field(default_factory=list)
    sources: List[SourceReference] = Field(default_factory=list)
    analysis: Dict[str, Any] = Field(default_factory=dict)
    critique: Dict[str, Any] = Field(default_factory=dict)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    workflow_plan: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowStatusResponse(BaseModel):
    """Status summary representation for a workflow."""
    workflow_id: str
    query: str
    workflow_status: str
    current_step: Optional[str] = None
    findings_count: int
    sources_count: int
    has_analysis: bool
    has_critique: bool
    has_report: bool
    critique_score: Optional[float] = None
    refinement_iterations: int
    agent_history_count: int
    error_count: int


class SystemInfoResponse(BaseModel):
    """Runtime diagnostics and LLM configuration."""
    version: str
    llm_provider: str
    model_name: str
    is_mock_mode: bool
    agents: List[Dict[str, str]]
    timestamp: str
