"""End-to-end integration tests for Multi-Agent Research Assistant API and workflow."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_api_health_and_info():
    """Verify system health, diagnostics, and workflow plan endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Health check
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

        # System info
        resp = await client.get("/api/system/info")
        assert resp.status_code == 200
        info = resp.json()
        assert "llm_provider" in info
        assert "agents" in info
        assert len(info["agents"]) == 5

        # Workflow plan
        resp = await client.get("/api/workflow-plan")
        assert resp.status_code == 200
        plan = resp.json()
        assert "stages" in plan
        assert "default_sequence" in plan
        assert plan["default_sequence"] == ["research", "analyze", "criticize", "write"]


@pytest.mark.asyncio
async def test_api_end_to_end_research():
    """Verify complete end-to-end research execution via POST /api/research."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "query": "Impact of generative AI on software development",
            "preferences": {"depth": "comprehensive"},
        }
        resp = await client.post("/api/research", json=payload)
        assert resp.status_code == 200

        data = resp.json()
        assert data["status"] == "completed"
        assert data["query"] == payload["query"]
        assert len(data["final_report"]) > 200
        assert len(data["agent_history"]) >= 5
        assert len(data["research_findings"]) > 0
        assert len(data["sources"]) > 0
        assert "themes" in data["analysis"]
        assert "quality_score" in data["critique"]

        workflow_id = data["workflow_id"]

        # Fetch workflow by ID
        get_resp = await client.get(f"/api/research/{workflow_id}")
        assert get_resp.status_code == 200
        fetched = get_resp.json()
        assert fetched["workflow_id"] == workflow_id
        assert fetched["query"] == payload["query"]
