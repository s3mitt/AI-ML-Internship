"""Workflow Planner for Multi-Agent Research Assistant.

Calculates stage sequencing, dependency graphs, and dynamic execution plans
with conditional refinement loops.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowStageDefinition(BaseModel):
    """Specification of an individual agent stage within the workflow graph."""
    stage_id: str
    name: str
    agent_name: str
    description: str
    dependencies: List[str] = Field(default_factory=list)
    reads_state_fields: List[str] = Field(default_factory=list)
    writes_state_fields: List[str] = Field(default_factory=list)
    is_conditional: bool = False


class WorkflowPlanner:
    """Computes and validates execution pipelines for multi-agent workflows."""

    @staticmethod
    def get_registered_stages() -> Dict[str, WorkflowStageDefinition]:
        """Returns standard declarative definition of all workflow stages."""
        return {
            "coordinator": WorkflowStageDefinition(
                stage_id="coordinator",
                name="Workflow Initialization & Governance",
                agent_name="Coordinator",
                description="Receives query, initializes shared state, plans execution, and supervises lifecycle.",
                dependencies=[],
                reads_state_fields=["query", "preferences"],
                writes_state_fields=["workflow_plan", "workflow_status"],
            ),
            "research": WorkflowStageDefinition(
                stage_id="research",
                name="Empirical Research Gathering",
                agent_name="Research Agent",
                description="Gathers facts, evidence, and catalogs primary source references.",
                dependencies=["coordinator"],
                reads_state_fields=["query", "preferences", "critique"],
                writes_state_fields=["research_findings", "sources", "research_notes"],
            ),
            "analyze": WorkflowStageDefinition(
                stage_id="analyze",
                name="Thematic Analysis & Synthesis",
                agent_name="Analyzer",
                description="Identifies themes, organizes evidence, and isolates facts from assumptions.",
                dependencies=["research"],
                reads_state_fields=["research_findings", "sources"],
                writes_state_fields=["analysis"],
            ),
            "criticize": WorkflowStageDefinition(
                stage_id="criticize",
                name="Peer Review & Quality Evaluation",
                agent_name="Critic",
                description="Validates evidence, scores quality, and flags gaps or refinement needs.",
                dependencies=["analyze"],
                reads_state_fields=["research_findings", "analysis"],
                writes_state_fields=["critique"],
            ),
            "refine": WorkflowStageDefinition(
                stage_id="refine",
                name="Targeted Refinement Loop",
                agent_name="Coordinator -> Research Agent / Analyzer",
                description="Conditional refinement stage triggered if Critic score is below threshold.",
                dependencies=["criticize"],
                reads_state_fields=["critique"],
                writes_state_fields=["research_findings", "analysis"],
                is_conditional=True,
            ),
            "write": WorkflowStageDefinition(
                stage_id="write",
                name="Report Generation & Critic Integration",
                agent_name="Writer",
                description="Synthesizes validated findings, analysis, and critic feedback into final Markdown report.",
                dependencies=["criticize"],
                reads_state_fields=["research_findings", "sources", "analysis", "critique"],
                writes_state_fields=["final_report", "report_metadata"],
            ),
        }

    @classmethod
    def get_linear_sequence(cls) -> List[str]:
        return ["research", "analyze", "criticize", "write"]
