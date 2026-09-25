# Multi-Agent Research Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat&logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.2-646CFF?style=flat&logo=vite)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-20%2F20%20Passing-success)](file:///D:/Linkific_Intern/Day%2022/backend/tests)

An autonomous multi-agent research pipeline that coordinates specialized AI agents through an explicit, strongly-typed Shared State object to produce comprehensive, peer-reviewed executive research reports.

---

## Overview

The **Multi-Agent Research Assistant** solves the fundamental limitations of single-prompt AI generation—such as cognitive overload, unverified claims, and hallucination propagation—by decomposing the investigation lifecycle into discrete, specialized roles:

$$\text{User Request} \longrightarrow \text{Coordinator} \longrightarrow \text{Research Agent} \longrightarrow \text{Analyzer} \longrightarrow \text{Critic} \longrightarrow \text{Writer} \longrightarrow \text{Final Report}$$

Each agent possesses strict input/output boundaries, communicates indirectly via a central **Shared State** blackboard, records execution telemetry in an audit history, and adheres to dynamic peer-critique feedback loops.

---

## Features

- **5 Specialized AI Agents:** Clear separation of concerns across Coordinator, Research Agent, Analyzer, Critic, and Writer.
- **Explicit Shared State:** Central `ResearchState` model that participates directly in the workflow and records complete agent execution history.
- **Observability & Audit Trail:** Every agent logs start/end timestamps, duration in seconds, input summaries, output summaries, and status.
- **Dynamic Peer Critique & Refinement:** The Critic evaluates empirical rigor and quality score (0–10). If score < 7.5, the Coordinator can automatically route execution back for refinement.
- **Dual Execution Engine:**
  - **Deterministic Local Mock Mode:** 100% reliable, fast, rich domain simulations out-of-the-box with zero paid API keys needed.
  - **Real LLM Mode:** Plug-and-play support for OpenAI (`gpt-4o`, `gpt-4o-mini`) and Google Gemini (`gemini-1.5-flash`).
- **Interactive Modern UI:** Responsive React + Vite dashboard featuring a live visual stepper, real-time agent activity feed, raw Shared State JSON inspector, and Markdown report export.
- **20 Comprehensive Automated Tests:** 100% passing test coverage verifying state mutations, agent guardrails, retries, and end-to-end API execution.

---

## Architecture

The system utilizes the **Blackboard Architectural Pattern** for decoupled agent communication and supervision:

```
[ User Request ]
       │
       ▼
 [ Coordinator ] ───(Plans workflow & manages lifecycle)
       │
       ├─► [ Research Agent ]  ──writes──► [ ResearchState ]
       │                                          ▲
       ├─► [ Analyzer ]        ◄──reads/writes────┤
       │                                          │
       ├─► [ Critic ]          ◄──reads/writes────┤
       │        │                                 │
       │        └─(Score < 7.5 ? Trigger Refinement Loop)
       │                                          │
       └─► [ Writer ]          ◄──reads/writes────┘
                │
                ▼
      [ Final Report Delivered ]
```

Detailed technical documentation is available in [docs/architecture.md](file:///D:/Linkific_Intern/Day%2022/docs/architecture.md).

---

## Agents

| Agent | Role | Input | Output |
| :--- | :--- | :--- | :--- |
| **Coordinator** | Entry point, workflow planner, retry coordinator, refinement director | Research query & preferences | Initialized state, stage sequence, execution audit |
| **Research Agent** | Empirical evidence gathering, source cataloging | Query & refinement instructions | Findings list, primary sources, research notes |
| **Analyzer** | Thematic synthesis, pattern detection, fact vs. assumption separation | Research findings & sources | Thematic breakdown, isolated facts, structured insights |
| **Critic** | Peer review, bias auditing, quality scoring (0–10), refinement signaling | Findings & analysis | Quality score, issues list, recommendations, refinement trigger |
| **Writer** | Executive document synthesis, citation linking, critic integration | Findings, sources, analysis, critique | Publication-grade Markdown report with references |

---

## Workflow

The workflow proceeds in six sequential phases with conditional refinement:

1. **Initialization:** Coordinator validates the query, assigns a unique `workflow_id`, and builds the stage sequence.
2. **Research Stage:** Research Agent extracts verified empirical findings with confidence scores and cataloged citations.
3. **Analysis Stage:** Analyzer synthesizes findings into macro themes and separates verifiable facts from working assumptions.
4. **Critique Stage:** Critic performs adversarial review, checks for logical fallacies and bias, and computes a quality score out of 10.
5. **Conditional Refinement Loop:** If quality score falls below 7.5, the Coordinator routes control back to Research Agent / Analyzer for targeted revision.
6. **Report Synthesis:** Writer compiles an executive Markdown report explicitly addressing all Critic recommendations and citing references.

Detailed Mermaid diagrams and sequence charts are available in [docs/workflow.md](file:///D:/Linkific_Intern/Day%2022/docs/workflow.md).

---

## Shared State

The workflow is governed by an explicit Pydantic model: [`ResearchState`](file:///D:/Linkific_Intern/Day%2022/backend/app/state/research_state.py).

```json
{
  "workflow_id": "wf_b8a391cd",
  "query": "Impact of generative AI on software development",
  "workflow_status": "completed",
  "workflow_plan": ["research", "analyze", "criticize", "write"],
  "current_step": null,
  "research_findings": [ ... ],
  "sources": [ ... ],
  "analysis": {
    "themes": [ ... ],
    "fact_vs_assumptions": { ... }
  },
  "critique": {
    "quality_score": 8.8,
    "passes_validation": true,
    "recommendations": [ ... ]
  },
  "final_report": "# Executive Research Report...",
  "agent_history": [
    {
      "agent": "Research Agent",
      "status": "completed",
      "duration_seconds": 0.015,
      "input_summary": "Query: 'Impact of generative AI...'",
      "output_summary": "Compiled 4 findings across 4 sources."
    }
  ],
  "errors": []
}
```

---

## Responsibility Matrix

A dedicated matrix documenting inputs, outputs, dependencies, communication paths, and state access permissions is located in [docs/responsibility-matrix.md](file:///D:/Linkific_Intern/Day%2022/docs/responsibility-matrix.md).

---

## Technology Stack

- **Backend:** Python 3.12, FastAPI, Pydantic V2, Uvicorn, HTTPX
- **Frontend:** React 18, Vite, Lucide React, Modern CSS Variables
- **Testing:** Pytest 9, pytest-asyncio, HTTPX ASGI Transport
- **AI / LLM Integration:** Abstracted `LLMService` with OpenAI, Gemini, and Local Deterministic Simulation Engine

---

## Project Structure

```
Day 22/
├── backend/
│   ├── app/
│   │   ├── agents/            # Coordinator, Research, Analyzer, Critic, Writer
│   │   ├── state/             # Shared state models & execution records
│   │   ├── workflow/          # Stage definitions, engine, and planner
│   │   ├── services/          # LLM service & mock engine
│   │   ├── models/            # API request/response DTOs
│   │   └── main.py            # FastAPI entry point & routes
│   ├── tests/                 # 20 automated unit & e2e tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/        # Header, TopicInput, WorkflowProgress, AgentActivity, etc.
│   │   ├── services/          # API client
│   │   ├── App.jsx            # Application shell
│   │   └── index.css          # Dark UI stylesheets
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── responsibility-matrix.md
│   ├── workflow.md
│   ├── architecture.md
│   └── demo.md
├── pytest.ini
├── .gitignore
└── README.md
```

---

## Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ (tested on Node v24)
- npm

### 1. Clone or Open Workspace
```bash
cd "D:\Linkific_Intern\Day 22"
```

### 2. Configure Backend Virtual Environment
```bash
python -m venv backend/venv
# Windows PowerShell
.\backend\venv\Scripts\Activate.ps1
# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env`:

```ini
# Provider options: "mock" (default), "openai", or "gemini"
LLM_PROVIDER=mock

# Optional API Keys (Only needed if LLM_PROVIDER is openai or gemini)
OPENAI_API_KEY=
GEMINI_API_KEY=

# Server Port
PORT=8000
HOST=0.0.0.0
```

---

## Running Backend

From `D:\Linkific_Intern\Day 22`:

```powershell
.\backend\venv\Scripts\uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI Swagger docs will be accessible at: `http://localhost:8000/docs`

---

## Running Frontend

From `D:\Linkific_Intern\Day 22\frontend`:

```powershell
npm run dev
```

Open your browser at: `http://localhost:5173`

---

## Running Tests

Run the complete test suite:

```powershell
cd "D:\Linkific_Intern\Day 22"
.\backend\venv\Scripts\pytest -v backend\tests
```

**All 20 tests pass in ~1.0s.**

---

## Example

### API Query:
```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Impact of generative AI on software development"}'
```

### Result:
- Workflow status: `completed`
- Research findings: 4 empirical facts cataloged
- Sources cited: McKinsey (2023), GitHub Research, IEEE S&P (2024), Stanford/CMU (2024)
- Themes identified: Productivity, Security & Governance, Agentic Paradigms
- Critic quality score: `8.8 / 10.0` (Approved)
- Full executive Markdown report generated and returned

---

## Mock Mode

By default, `LLM_PROVIDER=mock`. The system executes the full multi-agent pipeline using a deterministic, high-quality semantic simulation engine tailored to the domain. This guarantees that:
- The entire workflow can be demonstrated and graded with **zero cost and zero API credentials**.
- Tests execute with complete determinism in ~1 second.
- Offline evaluation is fully supported.

---

## Real LLM Mode

To run with real foundation models:
1. Set `LLM_PROVIDER=openai` and specify `OPENAI_API_KEY=sk-...` in `backend/.env` (or environment).
2. Or set `LLM_PROVIDER=gemini` and specify `GEMINI_API_KEY=...` in `backend/.env`.
3. Restart the backend server. The UI badge will immediately reflect `LLM: OPENAI` or `LLM: GEMINI`.

---

## Troubleshooting

- **Port 8000 already in use:** Specify a different port using `--port 8080` and update `frontend/vite.config.js` proxy.
- **PowerShell Script Execution Policy:** If running `Activate.ps1` gives an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
- **Node module warning:** The Vite application uses modern ESM modules. Run `npm run build` to confirm production bundle compilation.

---

## Future Improvements

1. **Live Web Crawling:** Connect the Research Agent to search APIs (e.g. Tavily, Brave Search) for real-time news retrieval.
2. **Heterogeneous Model Routing:** Dispatch Writer tasks to Claude 3.5 Sonnet, Analyzer tasks to GPT-4o, and Research tasks to Gemini 1.5 Pro.
3. **Vector State Memory:** Integrate ChromaDB or Qdrant for semantic caching and cross-investigation comparative studies.
4. **Interactive Human Review:** Enable human-in-the-loop overrides between the Critic and Writer stages.
