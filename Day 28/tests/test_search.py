import pytest
from search import (
    search_notes,
    summarize,
    split_sentences,
    compute_word_frequencies,
    score_sentences,
    DEFAULT_SUMMARY_SENTENCE_COUNT,
)


def test_search_notes():
    notes = [
        {"id": 1, "content": "Python is a great programming language."},
        {"id": 2, "content": "Rust is fast, but Python is versatile and Python is readable."},
        {"id": 3, "content": "JavaScript runs in the browser."},
    ]
    results = search_notes("Python", notes)
    assert len(results) == 2
    # Note 2 has "Python" twice, Note 1 has it once
    assert results[0]["id"] == 2
    assert results[1]["id"] == 1


def test_search_notes_empty_query():
    notes = [{"id": 1, "content": "Sample note content"}]
    assert search_notes("", notes) == []
    assert search_notes("   ", notes) == []


def test_search_notes_no_matches():
    notes = [{"id": 1, "content": "Sample note content"}]
    assert search_notes("golang", notes) == []


def test_search_notes_malformed_input():
    notes = [
        {"id": 1, "content": None},
        {"id": 2},
        {"id": 3, "content": "Valid note mentioning Python"},
    ]
    results = search_notes("Python", notes)
    assert len(results) == 1
    assert results[0]["id"] == 3


def test_split_sentences():
    text = "Hello world! How are you doing? I am doing well... This is a test."
    sentences = split_sentences(text)
    assert len(sentences) == 4
    assert sentences[0] == "Hello world"
    assert sentences[1] == "How are you doing"
    assert sentences[2] == "I am doing well"
    assert sentences[3] == "This is a test"

    assert split_sentences("") == []
    assert split_sentences("   ") == []


def test_compute_word_frequencies():
    text = "Data science with Python. Python is powerful and great for data analysis."
    freqs = compute_word_frequencies(text)
    assert freqs["python"] == 2
    assert freqs["data"] == 2
    # Stop words like 'with', 'for', 'and' should be excluded
    assert "with" not in freqs
    assert "for" not in freqs


def test_summarize_empty_and_short():
    assert summarize("") == ""
    assert summarize("   ") == ""

    short_text = "Single sentence note."
    assert summarize(short_text) == "Single sentence note."

    two_sentences = "First sentence. Second sentence."
    assert summarize(two_sentences, num_sentences=2) == "First sentence. Second sentence."


def test_summarize_extractive_selection():
    text = (
        "Artificial intelligence is transforming industries across the globe. "
        "Modern deep learning architectures power many artificial intelligence applications. "
        "Traditional software engineering remains critical for building reliable systems. "
        "Every developer should understand both software and intelligence systems."
    )
    summary = summarize(text, num_sentences=2)
    assert len(summary) > 0
    assert summary.endswith(".")
    # Ensure it selected top 2 sentences
    sentences = split_sentences(summary)
    assert len(sentences) == 2
