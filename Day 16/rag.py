"""
Basic RAG Pipeline — Company Documentation Q&A
================================================
Retrieval-Augmented Generation over Linkific's Tech Domain Internship
Onboarding document.

Pipeline stages:
    1. Documents   - load + clean the source doc
    2. Chunking    - sliding-window chunker (chunk size is the variable under test)
    3. Embeddings  - TF-IDF vectors (local, no model download / API key needed)
    4. Retrieval   - cosine similarity, top-k chunks
    5. LLM         - local extractive answer synthesizer (swappable, see bottom)
    6. Analysis    - run a 10-question eval set across 4 chunk sizes and compare

Run with:
    python rag_pipeline.py

Requires: pandas, scikit-learn  (pip install pandas scikit-learn)

Outputs (written next to this script):
    response_evaluation_table.csv     - per-question, per-chunk-size results
    chunk_size_comparison_summary.csv - aggregate metrics per chunk size
Plus a full run log printed to stdout (see bottom of this file for a sample).
"""

import re
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

pd.set_option("display.width", 140)
pd.set_option("display.max_colwidth", 60)

# --- FIX: anchor paths to this script's folder -------------------------
BASE_DIR = Path(__file__).resolve().parent
DOC_PATH = BASE_DIR / "Copy of Onboarding (Tech Domain).docx"
OUTPUT_DIR = BASE_DIR


# ----------------------------------------------------------------------
# 1. DOCUMENTS
# ----------------------------------------------------------------------
def extract_docx_text(path: Path) -> str:
    """Extract plain text from a .docx file without requiring external dependencies."""
    with zipfile.ZipFile(path) as z:
        xml_content = z.read("word/document.xml")
    root = ET.fromstring(xml_content)
    w_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    lines = []
    for p in root.iter(f"{{{w_ns}}}p"):
        parts = []
        for node in p.iter():
            if node.tag == f"{{{w_ns}}}t" and node.text:
                parts.append(node.text)
            elif node.tag == f"{{{w_ns}}}tab":
                parts.append(" ")
            elif node.tag == f"{{{w_ns}}}br":
                parts.append("\n")
        line = "".join(parts).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def load_document(path) -> str:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Document not found.\n"
            f"  Looked at : {path}\n"
            f"  Script dir: {BASE_DIR}\n"
            f"  CWD       : {Path.cwd()}\n"
            f"Make sure 'Copy of Onboarding (Tech Domain).docx' sits next to rag.py."
        )
    if path.suffix.lower() == ".docx":
        raw_text = extract_docx_text(path)
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
    return clean_text(raw_text)


def clean_text(t: str) -> str:
    """Strip markdown table pipes / heading markers / links so the plain
    text reads naturally for chunking and retrieval."""
    t = re.sub(r"\|", " ", t)
    t = re.sub(r"#+", "", t)
    t = re.sub(r"\*+", "", t)
    t = re.sub(r"_{3,}", "", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)  # markdown links -> plain text
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{2,}", "\n", t)
    return t.strip()


# ----------------------------------------------------------------------
# 2. CHUNKING
# ----------------------------------------------------------------------
def chunk_text(text: str, chunk_size: int, overlap: int):
    """Sliding-window character chunker."""
    step = max(chunk_size - overlap, 1)
    chunks = []
    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(text):
            break
    return chunks


CHUNK_CONFIGS = {
    "small_150":   {"chunk_size": 150,  "overlap": 30},
    "medium_300":  {"chunk_size": 300,  "overlap": 50},
    "large_600":   {"chunk_size": 600,  "overlap": 100},
    "xlarge_1200": {"chunk_size": 1200, "overlap": 150},
}


# ----------------------------------------------------------------------
# 3. EMBEDDINGS  (TF-IDF — local, no download/API key needed)
# ----------------------------------------------------------------------
def build_index(chunks):
    """Fit a TF-IDF vectorizer over the chunk set -> (vectorizer, chunk_matrix).

    Swap this for a real embedding model once you have internet/API access, e.g.:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        def build_index(chunks):
            return model, model.encode(chunks)
    """
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(chunks)
    return vectorizer, matrix


# ----------------------------------------------------------------------
# 4. RETRIEVAL
# ----------------------------------------------------------------------
def retrieve(query, vectorizer, matrix, chunks, top_k=3):
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, matrix).flatten()
    ranked_idx = sims.argsort()[::-1][:top_k]
    return [(chunks[i], float(sims[i])) for i in ranked_idx]


# ----------------------------------------------------------------------
# 5. LLM — answer generation (local extractive stand-in)
# ----------------------------------------------------------------------
def generate_answer(query, retrieved):
    """
    Local 'LLM' stand-in: ranks sentences from the retrieved chunks by
    term-overlap with the query and stitches the top matches into an answer.

    Swap the body of this function for a real LLM API call to upgrade from
    extractive to generative answers -- retrieval stays identical, e.g.:

        import anthropic
        client = anthropic.Anthropic(api_key="...")
        def generate_answer(query, retrieved):
            context = "\\n\\n".join(c for c, s in retrieved)
            msg = client.messages.create(
                model="claude-sonnet-4-6", max_tokens=300,
                messages=[{"role": "user", "content":
                    f"Answer using only this context.\\n\\nContext:\\n{context}\\n\\nQuestion: {query}"}],
            )
            return msg.content[0].text
    """
    query_terms = set(re.findall(r"[a-zA-Z]+", query.lower()))
    sentences = []
    for chunk, score in retrieved:
        # protect common title abbreviations (Mr./Ms./Dr.) from false sentence splits
        protected = re.sub(r"\b(Mr|Mrs|Ms|Dr)\.", r"\1<DOT>", chunk)
        for sent in re.split(r"(?<=[.!?])\s+", protected):
            sent = sent.replace("<DOT>", ".").strip()
            if len(sent) > 10:
                sentences.append((sent, score))

    scored = []
    for sent, chunk_score in sentences:
        sent_terms = set(re.findall(r"[a-zA-Z]+", sent.lower()))
        overlap = len(query_terms & sent_terms)
        scored.append((overlap * 2 + chunk_score, sent))
    scored.sort(key=lambda x: x[0], reverse=True)

    top_sents, seen = [], set()
    for _, s in scored:
        if s not in seen:
            top_sents.append(s)
            seen.add(s)
        if len(top_sents) >= 2:
            break

    return " ".join(top_sents) if top_sents else "I couldn't find relevant information in the document."


# ----------------------------------------------------------------------
# 6. PRACTICAL "ASK" HELPER (connect docs -> ask -> receive answer)
# ----------------------------------------------------------------------
def build_runtime_index(doc_text, chunk_size=300, overlap=50):
    chunks = chunk_text(doc_text, chunk_size, overlap)
    vectorizer, matrix = build_index(chunks)
    return chunks, vectorizer, matrix


def ask(question, chunks, vectorizer, matrix, top_k=3, verbose=True):
    retrieved = retrieve(question, vectorizer, matrix, chunks, top_k=top_k)
    answer = generate_answer(question, retrieved)
    if verbose:
        print("Q:", question)
        print("A:", answer)
        print(f"(retrieved {len(retrieved)} chunks, top similarity={retrieved[0][1]:.3f})\n")
    return answer


# ----------------------------------------------------------------------
# 7. EVALUATION SET
# ----------------------------------------------------------------------
EVAL_SET = [
    {"question": "What are the working days during the internship?",
     "expected_keywords": ["monday", "saturday"]},
    {"question": "How long is the internship duration?",
     "expected_keywords": ["4", "months"]},
    {"question": "What time is the Daily Tech Meet held?",
     "expected_keywords": ["8:00", "pm"]},
    {"question": "What three things must interns maintain during Month 1 training?",
     "expected_keywords": ["google sheet", "google doc", "github"]},
    {"question": "What is the minimum attendance required for the Certificate of Completion?",
     "expected_keywords": ["80%", "attendance"]},
    {"question": "How many days of leave are interns entitled to?",
     "expected_keywords": ["12", "days", "leave"]},
    {"question": "What email should be used to contact HR?",
     "expected_keywords": ["hr.linkific@gmail.com"]},
    {"question": "What should the GitHub repository be named?",
     "expected_keywords": ["linkific tasks"]},
    {"question": "Who is the CTO of Linkific?",
     "expected_keywords": ["aditya", "bondre", "cto"]},
    {"question": "What is the maximum time allowed per person to present updates in the Tech Meet?",
     "expected_keywords": ["4", "minutes"]},
]


def keyword_hit(text, keywords):
    text_l = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_l) / len(keywords)


def run_chunk_size_experiment(doc_text):
    results_rows = []
    for cfg_name, cfg in CHUNK_CONFIGS.items():
        chunks = chunk_text(doc_text, **cfg)
        vectorizer, matrix = build_index(chunks)
        for item in EVAL_SET:
            q, kws = item["question"], item["expected_keywords"]

            t0 = time.perf_counter()
            retrieved = retrieve(q, vectorizer, matrix, chunks, top_k=3)
            answer = generate_answer(q, retrieved)
            latency_ms = (time.perf_counter() - t0) * 1000

            retrieval_score = keyword_hit(" ".join(c for c, s in retrieved), kws)
            answer_score = keyword_hit(answer, kws)
            avg_sim = sum(s for _, s in retrieved) / len(retrieved)

            results_rows.append({
                "chunk_config": cfg_name,
                "chunk_size": cfg["chunk_size"],
                "num_chunks_in_doc": len(chunks),
                "question": q,
                "retrieval_keyword_recall": round(retrieval_score, 2),
                "answer_keyword_recall": round(answer_score, 2),
                "avg_similarity_top3": round(avg_sim, 3),
                "latency_ms": round(latency_ms, 2),
                "answer": answer,
            })
    return pd.DataFrame(results_rows)


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    print("=" * 70)
    print("STEP 1-2: LOAD DOCUMENT + CHUNKING PREVIEW")
    print("=" * 70)
    doc_text = load_document(DOC_PATH)
    print(f"Document length: {len(doc_text)} characters, {len(doc_text.split())} words\n")

    for name, cfg in CHUNK_CONFIGS.items():
        chunks = chunk_text(doc_text, **cfg)
        avg_len = sum(len(c) for c in chunks) // len(chunks)
        print(f"{name:12s} chunk_size={cfg['chunk_size']:5d}  -> {len(chunks):2d} chunks, avg length {avg_len}")

    print("\n" + "=" * 70)
    print("STEP 3-5: EMBEDDINGS + RETRIEVAL + LLM DEMO")
    print("=" * 70)
    chunks, vectorizer, matrix = build_runtime_index(doc_text, chunk_size=300, overlap=50)
    ask("What time is the Daily Tech Meet held?", chunks, vectorizer, matrix)
    ask("How many days of leave am I entitled to during the internship?", chunks, vectorizer, matrix)
    ask("What should I name my GitHub repository?", chunks, vectorizer, matrix)

    print("=" * 70)
    print("STEP 6: RAG RETRIEVAL PERFORMANCE ANALYSIS (chunk-size experiment)")
    print("=" * 70)
    results_df = run_chunk_size_experiment(doc_text)
    results_csv = OUTPUT_DIR / "response_evaluation_table.csv"
    results_df.to_csv(results_csv, index=False)
    print(f"Generated {len(results_df)} evaluation rows "
          f"({len(CHUNK_CONFIGS)} chunk sizes x {len(EVAL_SET)} questions)")
    print(f"Saved -> {results_csv}\n")

    summary = results_df.groupby(["chunk_config", "chunk_size", "num_chunks_in_doc"]).agg(
        avg_retrieval_recall=("retrieval_keyword_recall", "mean"),
        avg_answer_recall=("answer_keyword_recall", "mean"),
        avg_similarity=("avg_similarity_top3", "mean"),
        avg_latency_ms=("latency_ms", "mean"),
    ).round(3).reset_index().sort_values("chunk_size")
    summary_csv = OUTPUT_DIR / "chunk_size_comparison_summary.csv"
    summary.to_csv(summary_csv, index=False)
    print("Aggregate comparison across chunk sizes:")
    print(summary.to_string(index=False))
    print(f"\nSaved -> {summary_csv}\n")

    best_row = summary.loc[summary["avg_answer_recall"].idxmax()]
    print("=" * 70)
    print("BEST-PERFORMING CONFIGURATION")
    print("=" * 70)
    print(f"  {best_row['chunk_config']}  (chunk_size={int(best_row['chunk_size'])}, "
          f"{int(best_row['num_chunks_in_doc'])} chunks)")
    print(f"  avg_answer_recall    = {best_row['avg_answer_recall']}")
    print(f"  avg_retrieval_recall = {best_row['avg_retrieval_recall']}")
    print(f"  avg_latency_ms       = {best_row['avg_latency_ms']}")


if __name__ == "__main__":
    main()