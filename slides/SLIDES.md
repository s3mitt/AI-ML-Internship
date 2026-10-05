# Slide Deck: AI Incident Finder
**A Lightweight, Offline RAG System for AI Ethics & Safety Incidents**  
*Presented by: System Author & Lead Developer*

---

## Slide 1: Title & Overview
### AI Incident Finder
**Grounded Offline RAG with Deterministic Confidence Guardrails**

- **Author:** Sumit (AI Engineering Intern)
- **Core Technology:** scikit-learn TF-IDF, Cosine Similarity, Python 3.12
- **Key Proposition:** 100% Offline, Zero Cloud API Costs, Zero Hallucinations
- **Knowledge Domain:** Real-World AI Ethics, Bias, Privacy, and Safety Incidents

---

## Slide 2: The Problem
### The Danger of Ungrounded AI & Heavy RAG Architectures

- **Real-World Impact:** Teams repeatedly deploy biased or unsafe AI systems because historical incident lessons are inaccessible and siloed.
- **The Modern RAG Problem:**
  - Excessive complexity: Remote vector databases, cloud dependencies, expensive API keys.
  - High cold-start latency: 2–5 seconds per query on slow networks or large models.
  - The Hallucination Hazard: When queries are out-of-domain, standard RAG still forces generative LLMs to invent answers from irrelevant retrieved chunks.

---

## Slide 3: The Solution
### AI Incident Finder: Simple, Deterministic & Verifiable

- **Lightweight Knowledge Base:** Curated dataset of 8 landmark public AI incidents across Bias, Privacy, Hallucination, and Misinformation.
- **Pure Python & Scikit-Learn:** Sublinear TF-IDF representation with bigram tokenization and cosine similarity retrieval.
- **Empirical Confidence Guardrail:** Strict threshold ($\tau = 0.15$) immediately returns *"I don't have enough information to answer that"* for ungrounded queries.
- **Transparent Provenance:** Every response provides the canonical title, year, category, and exact similarity confidence score.
- **Dual Interface:** High-speed CLI (< 15ms) + lightweight Streamlit UI (< 25 lines of code).

---

## Slide 4: System Architecture
### Data Flow & Decision Pipeline

```text
[User Query]
      │
      ▼
[Preprocessing & Bigrams]
      │
      ▼
[TF-IDF Vectorization]
      │
      ▼
[Cosine Similarity vs Incident Corpus]
      │
      ▼
[Evaluate Best Score S_max]
      │
  ┌───┴───────────────────────────────┐
  │ S_max >= 0.15?                    │
  ├───┬───────────────────────────────┤
  │   ▼ YES                           ▼ NO
  │ [Grounded Answer Extraction]    [Guardrail Refusal]
  │ [Add Related Secondary Context] │ "I don't have enough
  │ [Attach Provenance Citations]   │  information to answer that."
  └───┬───────────────────────────────┴───┐
      ▼                                   ▼
 [Grounded CLI / Web Output]         [Zero-Citation Refusal]
```

---

## Slide 5: Tech Stack & Design Trade-Offs
### Pragmatic Engineering Decisions

| Component | Choice | Rationale | Trade-Off |
| :--- | :--- | :--- | :--- |
| **Language** | Python 3.12 | Standard AI ecosystem compatibility | Interpreted execution speed |
| **Retrieval** | Scikit-Learn TF-IDF | Instant cold start, zero API keys, CPU native | Exact vocabulary overlap required |
| **Similarity** | Cosine Similarity | Bounded $[-1, 1]$ metric, transparent scores | Linear scan over small matrix |
| **Guardrail** | Fixed Cutoff ($\tau = 0.15$) | Empirically derived boundary between signal and noise | Static across corpus shifts |
| **UI** | Streamlit (< 25 lines) | Decoupled presentation layer with zero bloat | Minimalist styling |

---

## Slide 6: Live Demonstration
### Verifying Retrieval, Multi-Context & Refusal Guardrail

- **Demo Case 1 (Bias):**  
  `python app.py "How did AI show bias in hiring resumes?"`  
  *Result: 15.65% Confidence | Amazon Resume Screener (2018) | Root cause & takeaway.*
- **Demo Case 2 (Hallucination):**  
  `python app.py "Lawyers submitting fake AI cases to court"`  
  *Result: 17.48% Confidence | Mata v. Avianca (2023) | Judicial sanction details.*
- **Demo Case 3 (Guardrail Refusal):**  
  `python app.py "What is the recipe for chocolate cake?"`  
  *Result: 0.00% Confidence (< 15%) | "I don't have enough information to answer that."*
- **Demo Case 4 (Web UI):**  
  `streamlit run streamlit_app.py`  
  *Interactive visual exploration with live confidence metrics.*

---

## Slide 7: Engineering Challenges & Test Verification
### Overcoming Obstacles & Ensuring Reliability

- **Challenge:** Vocabulary mismatch in short natural language queries.
  - *Solution:* Enriched corpus text (title + category + summary + lesson) + bigrams `(1, 2)` + sublinear term frequency scaling ($1 + \log tf$). Boosted relevant scores by 30%+.
- **Challenge:** Determining reliable guardrail separation without false positives.
  - *Solution:* Calibrated against 13 benchmark queries. Noise peaked at 0.0669; signal started at 0.1565. Set cutoff at 0.1500.
- **Automated Verification:**
  - 6 comprehensive `pytest` test cases covering schema, retrieval, guardrails, and malformed inputs.
  - **100% Pass Rate in 2.49 seconds** (documented in `docs/TEST_REPORT.md`).

---

## Slide 8: Future Roadmap & Production Scaling
### Path to an Enterprise-Ready Knowledge Engine

1. **Semantic Dense Embeddings:** Integrate local sentence transformers (`all-MiniLM-L6-v2`) for semantic search without keyword dependency.
2. **Hybrid Retrieval & Reranking:** Combine sparse BM25 and dense vectors via Reciprocal Rank Fusion (RRF) with a cross-encoder reranker.
3. **Local Small Language Model (SLM):** Pair with a local quantized model (e.g. Llama 3.2 1B via Ollama) with strict context injection for fluent summaries.
4. **Dataset Scaling & Persistent Storage:** Expand from 8 to 500+ incidents in SQLite / ChromaDB.
5. **Continuous Evaluation:** Establish CI/CD regression gates tracking Faithfulness and Context Recall via the Ragas framework.
