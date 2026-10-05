# 🛡️ AI Incident Finder

A lightweight, fully offline Retrieval-Augmented Generation (RAG) system that answers questions about real-world artificial intelligence ethics, bias, safety, and privacy incidents.

Built without external API keys, complex vector databases, or heavy neural dependencies, the engine relies on scikit-learn's TF-IDF vectorizer and cosine similarity. It retrieves grounded incident summaries, extracts key engineering takeaways, attributes exact source citations, and implements a confidence guardrail that says *"I don't have enough information to answer that"* when queries fall outside its knowledge base.

---

## 🌟 Key Features

- **100% Offline & Zero API Cost:** Runs completely locally on CPU in under 15ms per query without sending data to third-party endpoints.
- **Grounded Factual Retrieval:** Ranks curated real-world AI incidents using sublinear TF-IDF and bigram feature representations.
- **Confidence Guardrail:** Deterministic similarity threshold ($\tau = 0.15$) rejects out-of-domain queries to prevent ungrounded answers.
- **Dual Interface:** Clean CLI tool with colored output / JSON mode, plus an optional lightweight Streamlit web application (< 25 lines of code).
- **Comprehensive Source Attribution:** Returns incident titles, publication years, incident categories, and cosine similarity scores.

---

## 📁 Repository Structure

```text
D:/Linkific_Intern/Day 29/
├── app.py                      # Core RAG engine, TF-IDF indexer, CLI interface (~185 lines)
├── streamlit_app.py            # Streamlit web interface (24 lines)
├── requirements.txt            # Minimal Python dependencies
├── pytest.ini                  # Pytest configuration
├── .gitignore                  # Git ignore rules
├── data/
│   └── incidents.json          # 8 curated real-world AI ethics incident records
├── tests/
│   └── test_app.py             # 6 automated pytest tests verifying retrieval & guardrails
├── docs/
│   ├── ARCHITECTURE.md         # System design, Mermaid pipeline diagram, design tradeoffs
│   ├── TEST_REPORT.md          # Real test execution log and threshold calibration data
│   ├── INTERVIEW_QA.md         # 10 technical interview questions with 1st-person answers
│   ├── PRESENTATION_NOTES.md   # Slide-by-slide speaker notes (10-15 min) + elevator pitch
│   └── DEMO_PRACTICE_CHECKLIST.md # Rehearsal checklist, setup verification, contingency plans
├── demo/
│   ├── DEMO_SCRIPT.md          # 3-5 minute live demo walkthrough script
│   └── demo_output.txt         # Verified terminal outputs for offline demo backup
├── slides/
│   ├── presentation.pptx       # 8-slide presentation deck for mentors/interviewers
│   └── SLIDES.md               # Markdown version of the presentation slides
└── video/
    └── VIDEO_SCRIPT.md         # 2-3 minute timed video narration walkthrough
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.12.0)
- `pip` package manager

### 2. Installation
Clone or navigate to the project directory and install the requirements:
```bash
pip install -r requirements.txt
```

---

## 💻 Usage & Real Output Examples

### 1. Standard CLI Query (In-Domain Relevant)
```bash
python app.py "How did AI show bias in hiring resumes?"
```

**Real Output:**
```text
================================================================
QUERY: How did AI show bias in hiring resumes?
CONFIDENCE: 15.65% (Threshold: 15.00%)
================================================================

ANSWER:
Regarding 'Amazon Automated Resume Screening Tool Gender Bias' (2018): Amazon developed an internal machine learning recruiting engine to automate resume screening and identify top software engineering talent. The model was trained on resumes submitted to the company over a ten-year window. Because technology industry hiring was historically male-dominated, the algorithm learned to penalize candidate profiles containing the word 'women's' (such as 'women's chess club captain') and downgraded graduates of all-women's colleges. Engineers attempted to neutralize specific gender terms, but the model discovered correlated proxy terms. Amazon ultimately scrapped the system in 2018 before deployment because equal treatment could not be guaranteed.

Key Takeaway: Training algorithms on historical hiring data codifies and amplifies historical human biases; removing obvious demographic protected attributes is insufficient when proxy variables remain.

SOURCES:
  1. Amazon Automated Resume Screening Tool Gender Bias (2018) [BIAS] - Similarity: 15.65%
================================================================
```

### 2. Multi-Context Query (Cross-Incident Relevance)
```bash
python app.py "facial recognition discrimination and privacy breaches"
```

**Real Output:**
```text
================================================================
QUERY: facial recognition discrimination and privacy breaches
CONFIDENCE: 19.90% (Threshold: 15.00%)
================================================================

ANSWER:
Regarding 'Wrongful Arrest of Robert Williams via Facial Recognition' (2020): In Detroit, Michigan, Robert Williams was wrongfully arrested in front of his family for allegedly stealing luxury watches from a boutique store. Detroit Police Department detectives relied on automated facial recognition software that matched grainy surveillance video against a statewide driver's license database. The software flagged Williams despite noticeable physical differences between him and the actual suspect. The algorithm had known lower accuracy rates when evaluating darker skin tones. Investigators treated an unreliable probabilistic match as conclusive evidence without corroborating investigation, leading to unlawful overnight detention and civil rights violations.

Key Takeaway: Facial recognition technology displays significant disparate error rates across racial demographics and must never be used as sole probable cause without strict independent corroboration.

Related Context: In 2020, 'Clearview AI Mass Facial Biometrics Scraping and Data Breach' was another relevant incident involving privacy concerns: Mass indiscriminate harvesting of public personal data to generate biometric tracking vectors violates fundamental privacy rights and creates high-value honeypots for malicious actors.

SOURCES:
  1. Wrongful Arrest of Robert Williams via Facial Recognition (2020) [BIAS] - Similarity: 19.90%
  2. Clearview AI Mass Facial Biometrics Scraping and Data Breach (2020) [PRIVACY] - Similarity: 18.26%
================================================================
```

### 3. Out-of-Domain Guardrail Triggered (Refusal)
```bash
python app.py "What is the recipe for chocolate cake?"
```

**Real Output:**
```text
================================================================
QUERY: What is the recipe for chocolate cake?
CONFIDENCE: 0.00% (Threshold: 15.00%)
================================================================

I don't have enough information to answer that.

[Guardrail Active] Query similarity was below confidence threshold.
================================================================
```

### 4. Machine-Readable JSON Mode
```bash
python app.py "Samsung proprietary leak" --json
```

### 5. Interactive Mode
Run without arguments to enter an interactive shell:
```bash
python app.py
```

### 6. Streamlit Web Interface (Optional UI)
```bash
streamlit run streamlit_app.py
```

---

## 🧪 Testing

Execute the automated pytest suite:
```bash
pytest -v
```

All 6 test cases cover schema validation, exact in-domain matching, guardrail refusals, citation extraction, empty input handling, and custom threshold configurations. Refer to [`docs/TEST_REPORT.md`](file:///D:/Linkific_Intern/Day%2029/docs/TEST_REPORT.md) for full execution results.

---

## ⚠️ Limitations & Future Improvements

### Current Limitations:
1. **Lexical Matching:** TF-IDF relies on exact term overlap and n-grams. Queries using synonyms not found in the corpus (e.g., *"talent filtering prejudice"* vs *"hiring bias"*) may yield lower similarity scores.
2. **Fixed Curated Knowledge Base:** Contains 8 representative real-world AI incidents.
3. **Template Answer Synthesis:** Extracts verified text directly from matched documents rather than dynamically rephrasing with an autoregressive generative model.

### Roadmap for Production Scaling:
1. **Dense Vector Embeddings:** Integrate local sentence transformers (`all-MiniLM-L6-v2`) for semantic semantic retrieval.
2. **Hybrid Search & Reranking:** Combine sparse BM25 / TF-IDF with dense embeddings and a cross-encoder reranker.
3. **Local Small Language Model (SLM):** Connect to a quantized local model (such as Llama 3.2 1B or Gemma 2 2B via Ollama) to synthesize natural fluent responses while preserving citation grounding.
4. **Expanded Knowledge Base:** Scale to 500+ AI incidents indexed in SQLite or ChromaDB.
