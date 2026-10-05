"""AI Incident Finder - Offline RAG System.

Retrieves and answers questions about real-world AI ethics incidents using
scikit-learn TF-IDF vectorization and cosine similarity retrieval.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "incidents.json")
DEFAULT_THRESHOLD = 0.15
REFUSAL_MESSAGE = "I don't have enough information to answer that."


class IncidentRAG:
    """Offline Retrieval-Augmented Generation engine for AI incidents."""

    def __init__(self, data_path: str = DEFAULT_DATA_PATH, threshold: float = DEFAULT_THRESHOLD) -> None:
        """Initialize the RAG engine with dataset path and confidence threshold."""
        self.data_path = data_path
        self.threshold = threshold
        self.incidents: List[Dict[str, Any]] = self._load_data(data_path)
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            lowercase=True,
            sublinear_tf=True,
        )
        self._corpus: List[str] = []
        self._matrix = None
        self._build_index()

    def _load_data(self, path: str) -> List[Dict[str, Any]]:
        """Load and validate incidents from a JSON file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Incident database file not found at: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError(f"Invalid incident database: expected non-empty list in {path}")
        return data

    def _build_index(self) -> None:
        """Construct TF-IDF index across title, category, summary, and lesson fields."""
        self._corpus = [
            f"{item.get('title', '')} {item.get('category', '')} "
            f"{item.get('summary', '')} {item.get('lesson', '')}"
            for item in self.incidents
        ]
        self._matrix = self.vectorizer.fit_transform(self._corpus)

    def retrieve(self, query: str, top_k: int = 2) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieve top_k incidents matching the query using cosine similarity."""
        cleaned_query = query.strip()
        if not cleaned_query:
            return []

        query_vec = self.vectorizer.transform([cleaned_query])
        scores = cosine_similarity(query_vec, self._matrix)[0]

        top_indices = np.argsort(scores)[::-1][:top_k]
        results: List[Tuple[Dict[str, Any], float]] = []
        for idx in top_indices:
            results.append((self.incidents[idx], float(scores[idx])))
        return results

    def query(self, user_query: str, top_k: int = 2) -> Dict[str, Any]:
        """Execute RAG query with confidence guardrail and citation assembly."""
        stripped_query = user_query.strip()
        if not stripped_query:
            return {
                "query": user_query,
                "answer": REFUSAL_MESSAGE,
                "confidence": 0.0,
                "sources": [],
                "guardrail_triggered": True,
                "matches": [],
            }

        matches = self.retrieve(stripped_query, top_k=top_k)
        best_score = matches[0][1] if matches else 0.0

        # Guardrail check
        if not matches or best_score < self.threshold:
            return {
                "query": user_query,
                "answer": REFUSAL_MESSAGE,
                "confidence": round(best_score, 4),
                "sources": [],
                "guardrail_triggered": True,
                "matches": [],
            }

        top_incident = matches[0][0]
        sources = [
            {
                "title": inc["title"],
                "year": inc["year"],
                "category": inc.get("category", "general"),
                "similarity": round(score, 4),
            }
            for inc, score in matches
            if score >= (self.threshold * 0.5)  # include relevant secondary context
        ]

        # Synthesize grounded answer
        answer_parts = [
            f"Regarding '{top_incident['title']}' ({top_incident['year']}): "
            f"{top_incident['summary']}",
            f"Key Takeaway: {top_incident['lesson']}",
        ]
        if len(matches) > 1 and matches[1][1] >= self.threshold:
            sec_inc = matches[1][0]
            answer_parts.append(
                f"Related Context: In {sec_inc['year']}, '{sec_inc['title']}' was another relevant "
                f"incident involving {sec_inc.get('category', 'ethics')} concerns: {sec_inc['lesson']}"
            )

        return {
            "query": user_query,
            "answer": "\n\n".join(answer_parts),
            "confidence": round(best_score, 4),
            "sources": sources,
            "guardrail_triggered": False,
            "matches": [m[0] for m in matches],
        }

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format a query result dictionary into user-friendly CLI text."""
        lines = [
            "=" * 64,
            f"QUERY: {result['query']}",
            f"CONFIDENCE: {result['confidence']:.2%} (Threshold: {self.threshold:.2%})",
            "=" * 64,
        ]

        if result["guardrail_triggered"]:
            lines.append(f"\n{result['answer']}")
            lines.append("\n[Guardrail Active] Query similarity was below confidence threshold.")
        else:
            lines.append("\nANSWER:")
            lines.append(result["answer"])
            lines.append("\nSOURCES:")
            for idx, src in enumerate(result["sources"], start=1):
                lines.append(
                    f"  {idx}. {src['title']} ({src['year']}) "
                    f"[{src['category'].upper()}] - Similarity: {src['similarity']:.2%}"
                )

        lines.append("=" * 64)
        return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI Entry point for AI Incident Finder."""
    parser = argparse.ArgumentParser(
        description="AI Incident Finder: Offline RAG for AI Ethics & Safety Incidents"
    )
    parser.add_argument("query", nargs="?", help="Your question about AI incidents")
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Minimum cosine similarity threshold (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw JSON response instead of formatted text",
    )

    args = parser.parse_args(argv)

    try:
        rag = IncidentRAG(threshold=args.threshold)
    except Exception as exc:
        print(f"Error initializing IncidentRAG: {exc}", file=sys.stderr)
        return 1

    query_text = args.query
    if not query_text:
        print("AI Incident Finder (Interactive Mode - type 'exit' or 'quit' to end)")
        print(f"Loaded {len(rag.incidents)} incidents. Threshold: {rag.threshold:.2%}\n")
        while True:
            try:
                user_input = input("Enter your question: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break
            if not user_input or user_input.lower() in {"exit", "quit"}:
                break
            res = rag.query(user_input)
            print(rag.format_output(res))
            print()
        return 0

    result = rag.query(query_text)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(rag.format_output(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
