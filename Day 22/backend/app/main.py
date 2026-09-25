"""FastAPI Main Application for Multi-Agent Research Assistant.

Provides REST and SSE endpoints for initiating research workflows, observing real-time
agent execution telemetry, and retrieving verified research reports.
"""

from __future__ import annotations
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Load environment variables from .env
load_dotenv()

from .models.api_models import (
    ResearchRequest,
    ResearchResponse,
    SystemInfoResponse,
    WorkflowStatusResponse,
)
from .services.llm_service import get_llm_service
from .workflow.engine import get_workflow_engine
from .workflow.planner import WorkflowPlanner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("research_assistant")

app = FastAPI(
    title="Multi-Agent Research Assistant API",
    description="Collaborative multi-agent framework coordinating Research, Analysis, Critique, and Synthesis.",
    version="1.0.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["System"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "multi-agent-research-assistant",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/system/info", response_model=SystemInfoResponse, tags=["System"])
async def get_system_info() -> SystemInfoResponse:
    """Returns runtime diagnostic information and active LLM configuration."""
    llm = get_llm_service()
    agents = [
        {"name": "Coordinator", "role": "Workflow Planning, Orchestration, Refinement Routing"},
        {"name": "Research Agent", "role": "Empirical Information Gathering, Source Cataloging"},
        {"name": "Analyzer", "role": "Thematic Synthesis, Pattern Recognition, Fact Isolation"},
        {"name": "Critic", "role": "Peer Review, Consistency Checking, Quality Scoring"},
        {"name": "Writer", "role": "Executive Report Synthesis, Critic Integration"},
    ]
    return SystemInfoResponse(
        version="1.0.0",
        llm_provider=llm.provider,
        model_name=llm.model_name,
        is_mock_mode=llm.is_mock,
        agents=agents,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/api/workflow-plan", tags=["Workflow"])
async def get_workflow_plan() -> Dict[str, Any]:
    """Returns the declarative workflow graph with stages and dependencies."""
    stages = WorkflowPlanner.get_registered_stages()
    sequence = WorkflowPlanner.get_linear_sequence()
    return {
        "stages": {k: v.model_dump() for k, v in stages.items()},
        "default_sequence": sequence,
    }


@app.post("/api/research", response_model=ResearchResponse, tags=["Research"])
async def start_research(request: ResearchRequest) -> ResearchResponse:
    """Executes the full multi-agent research workflow synchronously and returns the final report."""
    engine = get_workflow_engine()
    logger.info(f"Received research request: '{request.query}'")
    try:
        state = await engine.execute_sync(query=request.query, preferences=request.preferences)
        return ResearchResponse(
            workflow_id=state.workflow_id,
            status=state.workflow_status,
            query=state.query,
            final_report=state.final_report,
            agent_history=state.agent_history,
            research_findings=state.research_findings,
            sources=state.sources,
            analysis=state.analysis,
            critique=state.critique,
            errors=state.errors,
            workflow_plan=state.workflow_plan,
            metadata=state.report_metadata,
        )
    except Exception as e:
        logger.error(f"Error processing research query '{request.query}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research workflow execution failed: {str(e)}",
        )


@app.post("/api/research/stream", tags=["Research"])
async def stream_research(request: ResearchRequest):
    """Executes the workflow while streaming live Server-Sent Events (SSE) telemetry to the UI."""
    engine = get_workflow_engine()
    logger.info(f"Received streaming research request: '{request.query}'")
    return StreamingResponse(
        engine.execute_streaming(query=request.query, preferences=request.preferences),
        media_type="text/event-stream",
    )


@app.get("/api/research/{workflow_id}", response_model=ResearchResponse, tags=["Research"])
async def get_workflow_details(workflow_id: str) -> ResearchResponse:
    """Fetches full state and report for a previously executed research workflow."""
    engine = get_workflow_engine()
    state = engine.get_state(workflow_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow with ID '{workflow_id}' not found.",
        )
    return ResearchResponse(
        workflow_id=state.workflow_id,
        status=state.workflow_status,
        query=state.query,
        final_report=state.final_report,
        agent_history=state.agent_history,
        research_findings=state.research_findings,
        sources=state.sources,
        analysis=state.analysis,
        critique=state.critique,
        errors=state.errors,
        workflow_plan=state.workflow_plan,
        metadata=state.report_metadata,
    )


@app.get("/api/workflows", tags=["Research"])
async def list_workflows() -> Dict[str, Any]:
    """Lists summary of all executed workflows in memory."""
    engine = get_workflow_engine()
    return engine.list_workflows()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
