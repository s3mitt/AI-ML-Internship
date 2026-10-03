"""Search and extractive summarization module for Smart Notes CLI."""

import logging
import re
from collections import Counter
from typing import Any

# Configure module-level logger
logger = logging.getLogger(__name__)

# Constants
DEFAULT_SUMMARY_SENTENCE_COUNT = 3
MIN_WORD_LENGTH = 3
COMMON_STOP_WORDS = frozenset({
    "the", "and", "is", "in", "to", "of", "a", "an", "that", "it",
    "for", "on", "with", "as", "this", "by", "at", "from", "be", "or",
    "are", "was", "were", "been", "have", "has", "had", "do", "does",
    "did", "but", "not", "what", "all", "were", "when", "we", "there",
    "can", "your", "which", "their", "if", "will", "so", "than"
})


def search_notes(keyword: str, notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Search notes for keyword occurrences, ranked by match count descending.

    Args:
        keyword: The query string to search for.
        notes: A list of note dictionaries containing 'content'.

    Returns:
        List of matching note dictionaries ordered by relevance.
    """
    clean_keyword = keyword.strip()
    if not clean_keyword:
        logger.warning("Empty search query provided.")
        return []

    query = clean_keyword.lower()
    ranked_notes: list[tuple[dict[str, Any], int]] = []

    for note in notes:
        content = note.get("content", "")
        if not isinstance(content, str):
            continue

        match_count = content.lower().count(query)
        if match_count > 0:
            ranked_notes.append((note, match_count))

    # Sort primarily by match count descending
    ranked_notes.sort(key=lambda item: item[1], reverse=True)
    return [note for note, _ in ranked_notes]


def split_sentences(text: str) -> list[str]:
    """Split input text into clean, non-empty sentences.

    Args:
        text: Source text to split.

    Returns:
        List of extracted sentence strings.
    """
    if not text or not text.strip():
        return []

    # Match sentences ending with punctuation or end of string
    raw_sentences = re.split(r'[.!?]+(?:\s+|$)', text.strip())
    clean_sentences = [sentence.strip() for sentence in raw_sentences if sentence.strip()]
    return clean_sentences


def compute_word_frequencies(text: str) -> Counter[str]:
    """Extract words and compute frequency table, filtering stop words and short tokens.

    Args:
        text: The source text for vocabulary frequency.

    Returns:
        A Counter mapping lowercase words to frequency counts.
    """
    words = re.findall(r'\b[a-zA-Z]{' + str(MIN_WORD_LENGTH) + r',}\b', text.lower())
    meaningful_words = [word for word in words if word not in COMMON_STOP_WORDS]
    return Counter(meaningful_words)


def score_sentences(
    sentences: list[str], word_frequencies: Counter[str]
) -> list[tuple[int, int, str]]:
    """Score sentences by accumulating word frequency counts.

    Args:
        sentences: List of candidate sentences.
        word_frequencies: Word frequency lookup table.

    Returns:
        List of tuples: (score, original_index, sentence_text).
    """
    scored_sentences: list[tuple[int, int, str]] = []
    for index, sentence in enumerate(sentences):
        words = re.findall(r'\b[a-zA-Z]{' + str(MIN_WORD_LENGTH) + r',}\b', sentence.lower())
        sentence_score = sum(word_frequencies[word] for word in words)
        scored_sentences.append((sentence_score, index, sentence))

    return scored_sentences


def summarize(
    text: str, num_sentences: int = DEFAULT_SUMMARY_SENTENCE_COUNT
) -> str:
    """Generate an extractive summary picking the top sentences by word frequency.

    Args:
        text: Note text to summarize.
        num_sentences: Maximum number of top sentences to include.

    Returns:
        Extractive summary preserving original sentence order.
    """
    sentences = split_sentences(text)
    if not sentences:
        return ""

    if len(sentences) <= num_sentences:
        return ". ".join(sentences) + "."

    word_frequencies = compute_word_frequencies(text)
    scored = score_sentences(sentences, word_frequencies)

    # Pick top sentences by score
    scored.sort(key=lambda item: item[0], reverse=True)
    top_candidates = scored[:num_sentences]

    # Restore chronological reading order
    top_candidates.sort(key=lambda item: item[1])

    summary_text = ". ".join(sentence for _, _, sentence in top_candidates)
    return summary_text + "."
