import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import DEFAULT_DATA_PATH, DEFAULT_THRESHOLD, REFUSAL_MESSAGE, IncidentRAG


@pytest.fixture
def rag_instance():
    """Fixture providing an initialized IncidentRAG instance."""
    return IncidentRAG(data_path=DEFAULT_DATA_PATH, threshold=DEFAULT_THRESHOLD)


def test_data_loads_correctly(rag_instance):
    """Test 1: Verify data loads properly with 8 valid incidents and required schema."""
    assert len(rag_instance.incidents) == 8
    required_keys = {"id", "title", "year", "category", "summary", "lesson"}
    for incident in rag_instance.incidents:
        assert required_keys.issubset(incident.keys())
        assert isinstance(incident["year"], int)
        assert len(incident["summary"].split()) >= 50
        assert incident["category"] in {"bias", "privacy", "misinformation", "hallucination"}


def test_relevant_result_for_known_question(rag_instance):
    """Test 2: Verify high-confidence relevant retrieval for known incident question."""
    query = "How did AI show bias in hiring resumes?"
    result = rag_instance.query(query)

    assert result["guardrail_triggered"] is False
    assert result["confidence"] >= rag_instance.threshold
    assert "Amazon" in result["answer"]
    assert len(result["sources"]) >= 1
    assert result["sources"][0]["title"] == "Amazon Automated Resume Screening Tool Gender Bias"
    assert result["sources"][0]["year"] == 2018


def test_refuses_unrelated_question(rag_instance):
    """Test 3: Verify guardrail triggers 'I don't have enough information' on irrelevant query."""
    irrelevant_query = "What is the secret recipe for homemade chocolate cake?"
    result = rag_instance.query(irrelevant_query)

    assert result["guardrail_triggered"] is True
    assert result["answer"] == REFUSAL_MESSAGE
    assert result["confidence"] < rag_instance.threshold
    assert result["sources"] == []


def test_citations_and_sources_returned(rag_instance):
    """Test 4: Verify structured citations with title, year, category, and similarity score."""
    query = "facial recognition discrimination and privacy breaches"
    result = rag_instance.query(query)

    assert result["guardrail_triggered"] is False
    assert len(result["sources"]) >= 1
    for src in result["sources"]:
        assert "title" in src
        assert "year" in src
        assert "category" in src
        assert "similarity" in src
        assert 0.0 <= src["similarity"] <= 1.0


def test_empty_and_whitespace_input_handled(rag_instance):
    """Test 5: Verify empty or whitespace-only inputs trigger guardrail without crashing."""
    for empty_input in ["", "   ", "\t\n  "]:
        result = rag_instance.query(empty_input)
        assert result["guardrail_triggered"] is True
        assert result["answer"] == REFUSAL_MESSAGE
        assert result["confidence"] == 0.0
        assert result["sources"] == []


def test_custom_threshold_and_error_handling():
    """Test 6: Verify custom threshold behavior and missing file error handling."""
    # Test strict threshold refusal
    strict_rag = IncidentRAG(threshold=0.95)
    result = strict_rag.query("How did AI show bias in hiring resumes?")
    assert result["guardrail_triggered"] is True
    assert result["answer"] == REFUSAL_MESSAGE

    # Test missing file error
    with pytest.raises(FileNotFoundError):
        IncidentRAG(data_path="data/non_existent_file.json")
