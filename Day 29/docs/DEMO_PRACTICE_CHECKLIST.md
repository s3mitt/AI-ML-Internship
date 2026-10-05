# Demo Practice & Rehearsal Checklist: AI Incident Finder

A systematic guide for practicing and delivering a seamless 3–5 minute live technical demonstration inside a 10–15 minute presentation to mentors and interviewers.

---

## 📋 1. Setup & Environment Verification Check (T - 2 Days)

- [ ] **Python Version Verification:** Verify Python 3.10+ is installed (`python --version`).
- [ ] **Dependencies Installed:** Run `pip install -r requirements.txt` and verify `scikit-learn`, `pytest`, `streamlit`, and `python-pptx` load without errors.
- [ ] **Working Directory Checked:** Ensure your terminal prompt is located in `D:\Linkific_Intern\Day 29`.
- [ ] **Clean Git Workspace:** Confirm git working tree is clean (`git status`).
- [ ] **Dataset Present & Valid:** Verify `data/incidents.json` has 8 incident objects.
- [ ] **Port Availability:** Ensure port 8501 is open for Streamlit (`netstat -ano | findstr 8501`).

---

## 🧪 2. Automated Test Run (T - 1 Day)

- [ ] Run the complete test suite:
  ```bash
  pytest -v
  ```
- [ ] Confirm all 6 test cases report `PASSED` in $< 3.0$ seconds.
- [ ] Review `docs/TEST_REPORT.md` to refresh memory on threshold numbers ($0.15$ cutoff, in-domain scores $0.1565–0.4687$, out-of-domain scores $\le 0.0669$).

---

## ⏱️ 3. Timed Rehearsals (Minimum 2 Required)

### Rehearsal #1: Full Presentation & Demo Run (Target: 11–13 min)
- [ ] **Start Timer** at Slide 1.
- [ ] Deliver 1-minute elevator pitch from memory without reading verbatim.
- [ ] Walk through Slides 1–5 in $< 5$ minutes.
- [ ] Switch smoothly to terminal at 05:00 for the Live Demo.
- [ ] Run Query 1: `python app.py "How did AI show bias in hiring resumes?"`
- [ ] Run Query 2: `python app.py "facial recognition discrimination and privacy breaches"`
- [ ] Run Query 3 (Guardrail Refusal): `python app.py "What is the recipe for chocolate cake?"`
- [ ] Launch Streamlit in browser: `streamlit run streamlit_app.py`
- [ ] Return to Slide 7 (Challenges & Tests) and Slide 8 (Roadmap) by 10:00.
- [ ] Conclude by 12:30.
- [ ] **Record actual rehearsal time:** `______ min ______ sec`.

### Rehearsal #2: Live Demo Focus & Glitch Recovery (Target: 3.5 min demo)
- [ ] Focus exclusively on the terminal transitions and explanations.
- [ ] Practice explaining **why** the confidence score is calculated as cosine similarity.
- [ ] Practice explaining **why** the guardrail fired on the chocolate cake query.
- [ ] Test intentional typo handling: verify the system behavior if you misspell a word.
- [ ] **Record actual demo time:** `______ min ______ sec`.

---

## 📸 4. Backup Evidence & Contingency Plan

If terminal execution fails during the live talk (e.g., terminal freezing, permission error):
- [ ] **Text Backup Prepared:** Verify `demo/demo_output.txt` is opened in a side editor tab.
- [ ] **Slide Backup Prepared:** Slide 6 in `slides/presentation.pptx` contains embedded output boxes showing the exact CLI and Streamlit outputs.
- [ ] **Pre-warmed Streamlit Tab:** Open `http://localhost:8501` in Chrome ahead of time so no delay occurs if launching during the talk.

---

## 🗣️ 5. Mentor Q&A Practice

Review the answers in `docs/INTERVIEW_QA.md` and practice verbalizing these common questions:
- [ ] *"Why did you use TF-IDF instead of embeddings?"* (Focus: zero API keys, no cold start, transparency, sub-15ms latency).
- [ ] *"How did you pick the 0.15 threshold?"* (Focus: calibration test, signal vs noise distribution, 0.0669 highest noise).
- [ ] *"What if a user asks using synonyms you don't have?"* (Focus: lexical limitation acknowledged, solution is hybrid search with MiniLM embeddings).
- [ ] *"How do you know it won't hallucinate?"* (Focus: deterministic extraction directly from curated incident text, no autoregressive generation).

---

## 🚀 6. Day-of Final Checklist (T - 15 Minutes)

- [ ] Close all unnecessary applications, notifications, and browser tabs.
- [ ] Set terminal font size to 16pt+ so mentors can read text clearly.
- [ ] Open PowerShell in `D:\Linkific_Intern\Day 29`.
- [ ] Run quick health check:
  ```bash
  python app.py "health check"
  ```
- [ ] Open `slides/presentation.pptx` in presentation mode (or `slides/SLIDES.md` in preview).
- [ ] Have a glass of water nearby.
- [ ] Take a deep breath: remember that the code, tests, and documentation are 100% verified!
