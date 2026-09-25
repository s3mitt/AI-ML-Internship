"""Unit tests for explicit Shared State object and lifecycle mutations."""

import pytest
from backend.app.state.research_state import (
    ResearchState,
    AgentExecutionRecord,
    Finding,
    SourceReference,
)


def test_shared_state_initialization():
    """Verify that ResearchState initializes with default values and custom fields."""
    state = ResearchState(
        query="Impact of quantum algorithms on RSA encryption",
        preferences={"domain": "Cryptography"},
        workflow_plan=["research", "analyze", "criticize", "write"],
    )

    assert state.query == "Impact of quantum algorithms on RSA encryption"
    assert state.preferences["domain"] == "Cryptography"
    assert state.workflow_status == "initialized"
    assert state.workflow_plan == ["research", "analyze", "criticize", "write"]
    assert state.research_findings == []
    assert state.sources == []
    assert state.analysis == {}
    assert state.critique == {}
    assert state.final_report == ""
    assert state.agent_history == []
    assert state.errors == []
    assert state.workflow_id.startswith("wf_")


def test_shared_state_history_recording():
    """Verify that adding execution records updates state history correctly."""
    state = ResearchState(query="Test Query")
    record = AgentExecutionRecord(
        agent="Research Agent",
        start_time="2026-09-25T10:00:00Z",
        end_time="2026-09-25T10:00:02Z",
        duration_seconds=2.0,
        status="completed",
        input_summary="Investigated Test Query",
        output_summary="Found 4 facts",
        step_index=1,
    )

    state.add_history(record)
    assert len(state.agent_history) == 1
    assert state.agent_history[0].agent == "Research Agent"
    assert state.agent_history[0].status == "completed"
    assert state.agent_history[0].duration_seconds == 2.0


def test_shared_state_error_recording():
    """Verify error tracking mechanism records structured error diagnostics."""
    state = ResearchState(query="Test Error Recording")
    state.add_error(
        agent="Analyzer",
        error_message="Network timeout while contacting analyzer service",
        error_type="TimeoutError",
        retry_count=1,
    )

    assert len(state.errors) == 1
    err = state.errors[0]
    assert err["agent"] == "Analyzer"
    assert err["error_type"] == "TimeoutError"
    assert err["retry_count"] == 1
    assert "timestamp" in err


def test_shared_state_lookups_and_summary():
    """Verify helper lookups for findings, sources, and high-level summary dict."""
    state = ResearchState(query="Lookup test")
    source = SourceReference(
        id="src_99",
        title="Test Journal",
        url_or_doi="https://doi.org/10.1234/test",
        author_or_org="Test Org",
        relevance_summary="Vital paper",
    )
    finding = Finding(
        id="fnd_99",
        title="Verified Theorem",
        fact="Shor's algorithm achieves polynomial time.",
        evidence="Theoretical proof",
        source_id="src_99",
    )

    state.sources.append(source)
    state.research_findings.append(finding)

    assert state.get_source_by_id("src_99") == source
    assert state.get_source_by_id("src_nonexistent") is None
    assert state.get_finding_by_id("fnd_99") == finding

    summary = state.to_summary_dict()
    assert summary["findings_count"] == 1
    assert summary["sources_count"] == 1
    assert summary["has_analysis"] is False
    assert summary["has_report"] is False
