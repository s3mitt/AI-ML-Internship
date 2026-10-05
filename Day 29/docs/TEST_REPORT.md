# Test Execution Report: AI Incident Finder

**Date:** 2026-10-05  
**Environment:** Python 3.12.0 (Windows x64)  
**Test Runner:** `pytest-9.1.1`  
**Target:** `IncidentRAG` in `app.py`  
**Dataset:** `data/incidents.json` (8 curated real-world AI incidents)

---

## 1. Test Summary

| Metric | Result |
| :--- | :--- |
| **Total Test Cases** | 6 |
| **Passed** | 6 |
| **Failed** | 0 |
| **Skipped** | 0 |
| **Duration** | 2.49s |
| **Status** | **100% PASS** |

---

## 2. Test Execution Output (Exact Terminal Log)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Sumit\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: D:\Linkific_Intern\Day 29
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.2, langsmith-0.14.0
collecting ... collected 6 items

tests/test_app.py::test_data_loads_correctly PASSED                      [ 16%]
tests/test_app.py::test_relevant_result_for_known_question PASSED        [ 33%]
tests/test_app.py::test_refuses_unrelated_question PASSED                [ 50%]
tests/test_app.py::test_citations_and_sources_returned PASSED            [ 66%]
tests/test_app.py::test_empty_and_whitespace_input_handled PASSED        [ 83%]
tests/test_app.py::test_custom_threshold_and_error_handling PASSED       [100%]

============================== 6 passed in 2.49s ==============================
```

---

## 3. Test Cases Specification & Verification

### Test 1: `test_data_loads_correctly`
- **Objective:** Ensure `data/incidents.json` loads cleanly and conforms to schema constraints.
- **Assertions:**
  - Database contains exactly 8 incidents.
  - Required keys present in each incident: `id`, `title`, `year`, `category`, `summary`, `lesson`.
  - Categories strictly belong to `{'bias', 'privacy', 'misinformation', 'hallucination'}`.
  - `summary` length exceeds 50 words for substantive context.
- **Outcome:** Passed.

### Test 2: `test_relevant_result_for_known_question`
- **Objective:** Verify accurate retrieval and answer synthesis for an in-domain query.
- **Query:** `"How did AI show bias in hiring resumes?"`
- **Assertions:**
  - `guardrail_triggered` is `False`.
  - Confidence score $\ge 0.15$ (observed: $0.1565$).
  - Top match identifies `"Amazon Automated Resume Screening Tool Gender Bias"` (2018).
  - Primary source citation returned with valid year and title.
- **Outcome:** Passed.

### Test 3: `test_refuses_unrelated_question`
- **Objective:** Verify out-of-domain guardrail prevents hallucinations and answers with fallback refusal.
- **Query:** `"What is the secret recipe for homemade chocolate cake?"`
- **Assertions:**
  - `guardrail_triggered` is `True`.
  - `answer == "I don't have enough information to answer that."`
  - Cosine similarity $< 0.15$ (observed: $0.0000$).
  - `sources` list is empty.
- **Outcome:** Passed.

### Test 4: `test_citations_and_sources_returned`
- **Objective:** Verify multi-incident retrieval returns structured citations with metadata and scores.
- **Query:** `"facial recognition discrimination and privacy breaches"`
- **Assertions:**
  - `guardrail_triggered` is `False`.
  - Sources contain `title`, `year`, `category`, and `similarity`.
  - Cosine similarities are bounded in $[0.0, 1.0]$.
  - Matches cross-domain incidents: Robert Williams arrest (Bias) + Clearview AI biometrics scraping (Privacy).
- **Outcome:** Passed.

### Test 5: `test_empty_and_whitespace_input_handled`
- **Objective:** Prevent edge-case crashes on empty, spaced, or control-character queries.
- **Inputs Evaluated:** `""`, `"   "`, `"\t\n  "`.
- **Assertions:**
  - System gracefully handles inputs without throwing exceptions.
  - `guardrail_triggered` is `True`.
  - Refusal message returned with confidence $0.0$.
- **Outcome:** Passed.

### Test 6: `test_custom_threshold_and_error_handling`
- **Objective:** Ensure modular parameter tuning and defensive exception handling.
- **Scenarios Evaluated:**
  - Strict threshold override ($0.95$) correctly suppresses answers for standard queries.
  - Initializing with a non-existent file path raises `FileNotFoundError`.
- **Outcome:** Passed.

---

## 4. Threshold Calibration Analysis

During empirical calibration across 13 benchmark queries, the cosine similarity scores demonstrated a distinct separation boundary:

| Query Type | Sample Query | Cosine Similarity | Action Taken |
| :--- | :--- | :--- | :--- |
| **In-Domain Relevant** | *"Healthcare algorithm biased against Black patients"* | **0.4687** | Answer & Cite |
| **In-Domain Relevant** | *"Facial recognition wrongful arrest in Detroit"* | **0.3280** | Answer & Cite |
| **In-Domain Relevant** | *"Google Bard telescope error stock drop"* | **0.2770** | Answer & Cite |
| **In-Domain Relevant** | *"Samsung proprietary code leak into chatgpt"* | **0.2459** | Answer & Cite |
| **In-Domain Relevant** | *"Lawyers submitting fake AI cases to court"* | **0.2246** | Answer & Cite |
| **In-Domain Relevant** | *"Fake news Pentagon explosion market crash"* | **0.1916** | Answer & Cite |
| **In-Domain Relevant** | *"Biometrics scraped without consent"* | **0.1732** | Answer & Cite |
| **In-Domain Relevant** | *"How did AI show bias in hiring resumes?"* | **0.1565** | Answer & Cite |
| **Irrelevant / Noise** | *"What is the weather like in New York today?"* | **0.0669** | Guardrail Refused |
| **Irrelevant / OOD** | *"What is the recipe for chocolate cake?"* | **0.0000** | Guardrail Refused |
| **Irrelevant / OOD** | *"Who won the soccer world cup in 1998?"* | **0.0000** | Guardrail Refused |
| **Irrelevant / OOD** | *"Quantum gravity in theoretical physics"* | **0.0000** | Guardrail Refused |
| **Irrelevant / OOD** | *"How do I fix a flat bicycle tire?"* | **0.0000** | Guardrail Refused |

**Conclusion:**  
A cutoff threshold of **$\tau = 0.15$** achieves 100% precision on this evaluation sample, accepting all relevant queries while rejecting non-AI or general knowledge queries.
