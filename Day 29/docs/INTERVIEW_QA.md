# Technical Interview Q&A: AI Incident Finder

Prepared from the perspective of the system author and lead developer. Each answer is written in the first person, structured in 3 to 5 concise sentences, followed by an actionable one-line takeaway.

---

### Question 1: What is Retrieval-Augmented Generation (RAG), and how did you implement it here?
**Answer:**  
In this project, I implemented RAG as a two-stage information pipeline: retrieval and answer synthesis. When a user submits a natural language question, the system transforms it into a numerical feature vector, retrieves the top matching records from a curated dataset of real-world AI incidents using cosine similarity, and builds a grounded response citing exact sources. Because this is a lightweight, fully offline system, I replaced the traditional neural LLM generator with a deterministic synthesis engine that extracts the incident summary and engineering takeaways directly from the retrieved documents. This guarantees that every answer is factually grounded without any risk of hallucination.  
**Key Takeaway:** *RAG couples dynamic search retrieval with answer synthesis to ground system outputs in authoritative source documents.*

---

### Question 2: Why did you choose TF-IDF with cosine similarity instead of dense neural embeddings and a vector database?
**Answer:**  
I selected TF-IDF and scikit-learn because the project objectives prioritized an ultra-fast, zero-dependency, fully offline architecture that runs reliably on standard CPUs without API keys or GPU memory. For a focused corpus of curated incident summaries, lexical retrieval with bigram tokenization captures technical keywords like "resume screening" and "facial recognition" exceptionally well with sub-15ms latency. Introducing an external vector database like Chroma or Pinecone would have added unnecessary infrastructure complexity, network latency, and deployment overhead for an 8-document knowledge base. TF-IDF provides mathematically transparent scoring where every term's contribution is directly inspectable.  
**Key Takeaway:** *Pick the simplest technology that solves the problem robustly; lexical search provides zero-cost, deterministic transparency for focused domain datasets.*

---

### Question 3: How did you determine the confidence threshold for the refusal guardrail?
**Answer:**  
I determined the threshold of 0.15 through empirical calibration against a benchmark of thirteen sample queries spanning in-domain questions and adversarial out-of-domain prompts. Relevant questions regarding hiring bias, legal hallucinations, and biometric breaches scored between 0.1565 and 0.4687, while completely unrelated questions like recipes or general trivia scored 0.0000. The highest-scoring false positive in my benchmark was a weather query that hit 0.0669 due to minor stopword overlap. Setting the threshold at 0.15 created a clean safety margin that reliably separates relevant signal from noise.  
**Key Takeaway:** *Guardrail thresholds must be calibrated empirically by observing score distributions across both target queries and adversarial negative controls.*

---

### Question 4: How did you test the system to ensure reliability?
**Answer:**  
I authored a six-part automated test suite using `pytest` that evaluates data integrity, algorithmic correctness, and edge-case handling. The tests verify that the incident schema contains required metadata, validate that known in-domain questions return expected titles and confidence scores, and confirm that irrelevant queries trigger the guardrail refusal. I also specifically tested adversarial inputs like empty strings and whitespace to prevent runtime crashes, as well as strict custom threshold overrides. All six tests execute cleanly in under 2.5 seconds, ensuring regression protection across changes.  
**Key Takeaway:** *Thorough testing must cover both happy-path retrieval accuracy and defensive edge cases like malformed inputs and out-of-domain refusals.*

---

### Question 5: How is the codebase structured, and what makes it maintainable?
**Answer:**  
I designed the codebase with modular separation of concerns centered around the `IncidentRAG` class in `app.py`. The class encapsulates data ingestion, index vectorization, retrieval ranking, guardrail evaluation, and output formatting behind clean, typed methods. Because the core engine is decoupled from the user interface, it seamlessly powers the CLI tool, the automated test suite, and a Streamlit web application written in under 25 lines. This decoupled architecture allows any single component—such as the vectorizer or storage layer—to be upgraded independently without breaking interfaces.  
**Key Takeaway:** *Decoupling the retrieval core from presentation layers ensures reusability across CLI, web interfaces, and automated test runners.*

---

### Question 6: What was the biggest engineering challenge you encountered while building this?
**Answer:**  
The biggest challenge was tuning the retrieval pipeline to handle short user questions that lacked exact keyword matches with the incident titles. With unigram TF-IDF alone, queries like "lawyers submitting fake AI cases" had diluted similarity scores because legal jargon differed slightly from the source summary. I resolved this by expanding the vectorizer to use bigrams `(1, 2)`, enabling sublinear term frequency scaling, and concatenating the incident's title, category, summary, and lesson into a unified corpus document. This adjustment boosted the similarity scores of relevant queries by over 30%, making threshold boundary separation distinct.  
**Key Takeaway:** *Enriching searchable document representations with bigrams and sublinear scaling significantly bridges vocabulary mismatch in lexical retrieval.*

---

### Question 7: What are the current architectural limitations of this implementation?
**Answer:**  
The primary limitation is lexical brittleness: because TF-IDF relies on token overlap, queries phrased with synonyms that do not exist in the corpus can fail to meet the 0.15 threshold. Additionally, the knowledge base is currently statically loaded from an in-memory JSON file of eight incidents, which does not support live document additions or real-time streaming updates. Lastly, the answer generation is extractive and deterministic rather than generative, meaning it cannot synthesize novel multi-document comparative narratives on the fly. These limitations are intentional trade-offs to keep the footprint tiny and zero-cost, but they represent clear boundaries for scaling.  
**Key Takeaway:** *Lexical search is bounded by vocabulary overlap and static corpus size, which sets clear priorities for future architectural iterations.*

---

### Question 8: How would you upgrade the retrieval layer with semantic embeddings and reranking?
**Answer:**  
To upgrade retrieval, I would integrate a compact open-source sentence transformer such as `all-MiniLM-L6-v2` via Hugging Face to generate 384-dimensional dense vectors for both queries and documents. I would then implement a hybrid search architecture that combines sparse BM25 scores with dense cosine similarity using Reciprocal Rank Fusion (RRF). Finally, I would add a cross-encoder model like `ms-marco-MiniLM-L-6-v2` to rerank the top 10 retrieved candidates, evaluating query-document pairs simultaneously for deep semantic context. This hybrid approach would eliminate synonym mismatch while maintaining fast inference speeds.  
**Key Takeaway:** *A two-stage hybrid pipeline combining sparse lexical search, dense semantic embeddings, and cross-encoder reranking yields optimal retrieval accuracy.*

---

### Question 9: How would you integrate a generative LLM for answer synthesis while preventing hallucinations?
**Answer:**  
I would connect the retrieval pipeline to a small, quantized local model like Llama-3.2-1B or Gemma-2-2B running locally through Ollama or llama.cpp to preserve the 100% offline requirement. The retrieved incident text would be injected into a strictly constrained system prompt instructing the model to answer exclusively using the provided context and output explicit bracketed citations. I would enforce a post-generation citation check that cross-references all claims against the source spans and triggers the refusal message if the model attempts to generate unsupported facts. This retains the conversational fluency of generative AI while enforcing strict grounding.  
**Key Takeaway:** *Pairing local quantized models with strict context-injected prompt constraints and automated citation verification preserves grounding.*

---

### Question 10: How would you scale the dataset and establish an automated evaluation framework?
**Answer:**  
To scale the dataset, I would migrate storage from `incidents.json` to an embedded SQLite or DuckDB database paired with an HNSW vector index in ChromaDB or FAISS, supporting thousands of incidents. For evaluation, I would build an automated test harness using the Ragas or TruLens framework with fifty curated (question, ground_truth_context, ground_truth_answer) pairs. I would track four core quantitative metrics across every release: Context Precision, Context Recall, Faithfulness, and Answer Relevance. This would transform qualitative ad-hoc testing into a continuous CI/CD evaluation gate.  
**Key Takeaway:** *Production scaling requires embedded persistent storage and continuous quantitative RAG evaluation using metrics like Faithfulness and Context Recall.*
