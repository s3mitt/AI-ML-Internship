# Presentation Notes & Speaker Guide: AI Incident Finder

**Target Duration:** 10–15 minutes (including a 3–5 minute live demonstration)  
**Presenter Perspective:** Project Author & Lead Engineer (First Person)

---

## ⏱️ Presentation Timing Breakdown

| Section | Topic | Allocated Time | Target Cumulative |
| :--- | :--- | :--- | :--- |
| **Intro** | 1-Minute Elevator Pitch & Title | 1:00 | 1:00 |
| **Slide 2** | The Problem: Ungrounded AI & Heavy RAG | 1:30 | 2:30 |
| **Slide 3** | The Solution: Offline AI Incident Finder | 1:30 | 4:00 |
| **Slide 4** | System Architecture & Information Pipeline | 2:00 | 6:00 |
| **Slide 5** | Tech Stack & Engineering Trade-Offs | 1:30 | 7:30 |
| **Slide 6** | **Live Terminal & Web Demonstration** | **3:30** | **11:00** |
| **Slide 7** | Engineering Challenges & Test Verification | 1:30 | 12:30 |
| **Slide 8** | Production Roadmap & Future Improvements | 1:30 | 14:00 |
| **Q&A** | Mentor Questions & Discussion | 1:00+ | 15:00 |

---

## 🎙️ 1-Minute Elevator Pitch

> *"Hello mentors and colleagues. As artificial intelligence systems become ubiquitous, understanding how they fail—through bias, hallucination, or data privacy breaches—is vital for every engineer building safe software. However, most modern RAG systems require external cloud API keys, heavy neural dependencies, and complex vector databases, and they still frequently hallucinate when asked questions outside their domain.*  
>  
> *To solve this, I built **AI Incident Finder**: a lightweight, 100% offline, zero-API-cost RAG system that answers questions about real-world AI ethics incidents. Using scikit-learn's TF-IDF vectorization and cosine similarity, it retrieves grounded historical incidents, extracts lessons, attributes exact source citations, and enforces an empirical confidence guardrail that firmly refuses out-of-domain queries by saying 'I don't have enough information to answer that.' It runs in under 15 milliseconds on any CPU and includes both a robust CLI and an intuitive Streamlit interface in under 25 lines of code."*

---

## 📊 Slide-by-Slide Speaker Notes

### Slide 1: Title & Introduction
- **Slide Content:** Project Title, Author Name, Tagline ("Lightweight Offline RAG for AI Ethics & Safety Incidents").
- **Time:** 1:00
- **Speaker Script:**  
  *"Good morning everyone. Today I'm excited to present AI Incident Finder, a project I developed to bridge practical RAG concepts with real-world AI ethics and safety lessons. My goal was to create a clean, reproducible, and verifiable information retrieval system that demonstrates the foundational mechanics of RAG—retrieval, confidence calibration, citation attribution, and refusal guardrails—without relying on black-box external cloud APIs or heavyweight infrastructure."*

---

### Slide 2: The Problem
- **Slide Content:** The dual challenges: Understanding AI failures and the bloat/hallucination risk of modern RAG setups.
- **Time:** 1:30
- **Speaker Script:**  
  *"Let's talk about the problems this addresses. First, software teams frequently repeat catastrophic AI mistakes—like training resume screeners on biased historical data or letting chatbots hallucinate legal citations in federal court—because case studies aren't easily queryable.*  
  *Second, modern RAG tutorials often over-engineer simple retrieval tasks. They force developers to set up remote vector databases, obtain paid API keys, and load massive transformer weights just to search a few documents. Worse, when an end-user asks an unrelated question, standard RAG setups still force the LLM to hallucinate an answer based on irrelevant retrieved chunks. I wanted to build an answer to both problems: a fast, transparent knowledge base that knows when to say 'I don't know'."*

---

### Slide 3: The Solution
- **Slide Content:** AI Incident Finder features: 100% offline, TF-IDF + cosine similarity, confidence threshold guardrail, exact citations, dual interface.
- **Time:** 1:30
- **Speaker Script:**  
  *"My solution is AI Incident Finder. It's a completely offline Python application that ingests a curated database of real-world AI ethics incidents. It computes sublinear TF-IDF vectors with bigram modeling, retrieves the top-ranking incidents using cosine similarity, extracts the key summary and engineering lesson, and outputs transparent source citations with similarity percentages.*  
  *Most importantly, I built a deterministic confidence guardrail. If the best match falls below our calibrated threshold of 15%, the system immediately refuses to guess, ensuring zero hallucinations."*

---

### Slide 4: System Architecture & Data Flow
- **Slide Content:** Mermaid Flowchart: User Query -> Bigram Preprocessing -> TF-IDF Vectorization -> Cosine Similarity -> Threshold Guardrail Check -> Grounded Answer Synthesis & Citations.
- **Time:** 2:00
- **Speaker Script:**  
  *"Here is the architecture of how a question flows through the system. When a query arrives, it is preprocessed and converted into a sparse TF-IDF vector using both unigrams and bigrams. This vector is compared against our pre-indexed incident corpus matrix using cosine similarity.*  
  *At this decision point, the system evaluates the maximum similarity score against our 0.15 threshold. If the score is below 0.15, the query is marked out-of-domain, the guardrail triggers, and the system gracefully halts without inventing facts.*  
  *If the score meets or exceeds 0.15, the top incident is selected for primary answer extraction, and if a secondary incident is also above threshold, it is integrated as related context. Finally, metadata citations are attached and formatted for output."*

---

### Slide 5: Tech Stack & Engineering Trade-Offs
- **Slide Content:** Python 3.12, scikit-learn, NumPy, Pytest, Streamlit; Design Trade-offs table.
- **Time:** 1:30
- **Speaker Script:**  
  *"I intentionally kept the tech stack lean. The core engine uses scikit-learn and NumPy. I chose TF-IDF over dense embeddings because it gives us instant cold-start execution, zero network calls, zero API costs, and full mathematical interpretability. We can inspect exactly which tokens drove the similarity score.*  
  *For presentation, I decoupled the engine so that `app.py` serves as both a high-performance CLI tool and an importable module. This allowed me to build the entire Streamlit web UI in just 24 lines of clean, readable code."*

---

### Slide 6: Live Demonstration (3–5 Minutes)
- **Slide Content:** Live terminal demo and Streamlit walkthrough.
- **Time:** 3:30
- **Speaker Script:**  
  *(Switch to terminal and run exact commands from `demo/DEMO_SCRIPT.md`)*  
  1. *"First, let's ask a direct question about hiring bias:*  
     `python app.py "How did AI show bias in hiring resumes?"`  
     *Notice the confidence score of 15.65%, the immediate retrieval of the 2018 Amazon resume screening incident, the extracted lesson, and the exact citation.*  
  2. *"Second, let's test a cross-incident query that spans both bias and privacy:*  
     `python app.py "facial recognition discrimination and privacy breaches"`  
     *Here, the engine retrieves two incidents: the Robert Williams wrongful arrest in Detroit and Clearview AI's mass biometrics scraping, providing related context.*  
  3. *"Third, let's test the guardrail with an adversarial out-of-domain question:*  
     `python app.py "What is the recipe for chocolate cake?"`  
     *Notice the similarity is 0.00%, the guardrail immediately activates, and it outputs our refusal message without guessing.*  
  4. *"Finally, we can launch the optional Streamlit interface:*  
     `streamlit run streamlit_app.py`  
     *It provides the exact same robust behavior in an interactive browser interface."*

---

### Slide 7: Engineering Challenges & Test Verification
- **Slide Content:** Challenge: Vocabulary mismatch & threshold calibration; Test Suite results: 6/6 tests passing in 2.49s.
- **Time:** 1:30
- **Speaker Script:**  
  *"During development, my biggest challenge was vocabulary mismatch. In a small corpus, standard unigram search struggled when questions didn't match the exact wording of the titles. I solved this by adding bigrams and sublinear term frequency scaling, which boosted relevant query scores by over 30%.*  
  *To prove reliability, I built an automated pytest suite with six comprehensive test cases covering schema validation, guardrail refusals, citation structures, whitespace inputs, and threshold overrides. All six tests run in under 2.5 seconds with 100% pass rate, documented in our test report."*

---

### Slide 8: Future Roadmap & Conclusion
- **Slide Content:** Scaling to dense embeddings (MiniLM), hybrid search (BM25 + Dense), local quantized LLM (Llama 3.2 1B), automated Ragas evaluation.
- **Time:** 1:30
- **Speaker Script:**  
  *"Looking forward to a production release, the roadmap is clear. First, I would introduce a local sentence transformer like `all-MiniLM-L6-v2` for dense semantic search and combine it with BM25 using Reciprocal Rank Fusion. Second, I would connect a local quantized SLM like Llama-3.2-1B via Ollama to generate conversational prose while enforcing strict context constraints. Finally, I would scale the database to hundreds of incidents in SQLite and implement automated evaluation metrics like Faithfulness and Context Recall using Ragas.*  
  *Thank you for your time, and I'd be delighted to answer any questions!"*
