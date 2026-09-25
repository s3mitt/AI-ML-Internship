# Architecture Notes: Multi-Agent Research Assistant

This document provides an exhaustive technical analysis of the architectural design, agent coordination paradigms, data models, fault tolerance mechanisms, and engineering decisions implemented in the **Multi-Agent Research Assistant**.

---

## 1. System Overview

The **Multi-Agent Research Assistant** is an autonomous distributed agentic pipeline designed to produce executive-grade, peer-reviewed research reports from arbitrary user queries. 

Rather than relying on a single large language model prompt (which suffers from cognitive overload, hallucination cascade, and unverified assumptions), the system decomposes the research lifecycle into five specialized, decoupled AI agents coordinated by an explicit Shared State object:

1. **Coordinator:** Master orchestrator, planner, and state supervisor.
2. **Research Agent:** Information harvester and empirical evidence collector.
3. **Analyzer:** Thematic pattern extractor and fact-versus-assumption demarcator.
4. **Critic:** Adversarial peer reviewer, quality scoring authority, and refinement director.
5. **Writer:** Executive report synthesizer incorporating peer critique into Markdown.

---

## 2. Agent Architecture

All agents in the system inherit from the common abstract base class [`BaseAgent`](file:///D:/Linkific_Intern/Day%2022/backend/app/agents/base_agent.py). This enforces a uniform lifecycle across all agents:

```
execute(state, step_index)
  │
  ├── 1. Capture Start Timestamp (ISO 8601) & High-Resolution Timer
  ├── 2. Generate Input Summary
  ├── 3. Execute Internal _process(state) Logic
  ├── 4. Generate Output Summary & Compute Duration
  ├── 5. Append AgentExecutionRecord to state.agent_history
  └── 6. Return Mutated ResearchState (or Record Error on Exception)
```

By abstracting lifecycle telemetry into `BaseAgent`, individual agents focus purely on their core business logic without repeating logging, error recording, or timing code.

---

## 3. Coordinator Responsibilities

The [`Coordinator`](file:///D:/Linkific_Intern/Day%2022/backend/app/agents/coordinator.py) serves as the brain of the workflow. Its responsibilities include:

- **State Genesis:** Creates an immutable `workflow_id` and initial [`ResearchState`](file:///D:/Linkific_Intern/Day%2022/backend/app/state/research_state.py).
- **Plan Generation:** Constructs the ordered execution DAG (`workflow_plan`).
- **Sequential Dispatch:** Triggers each agent in compliance with dependency preconditions.
- **Dynamic Feedback Loop Evaluation:** Inspects `state.critique` after the Critic stage. If `needs_refinement == True`, branches execution to refine research and re-analyze prior to writing.
- **Telemetry Streaming:** Emits progress events to UI consumers via Server-Sent Events (SSE).
- **Error Guardrails:** Prevents partial or failed runs from silently emitting corrupt reports.

---

## 4. Shared State Architecture

The system avoids passing ad-hoc dictionaries or loose strings. Instead, it employs an explicit, strongly-typed Pydantic model: [`ResearchState`](file:///D:/Linkific_Intern/Day%2022/backend/app/state/research_state.py).

### Schema Blueprint

```python
class ResearchState(BaseModel):
    workflow_id: str
    query: str
    preferences: Dict[str, Any]
    
    # Workflow Governance
    workflow_status: str          # "initialized" | "running" | "completed" | "failed"
    workflow_plan: List[str]      # ["research", "analyze", "criticize", "write"]
    current_step: Optional[str]
    refinement_iterations: int
    max_refinements: int
    
    # Stage Deliverables
    research_findings: List[Finding]
    sources: List[SourceReference]
    research_notes: str
    analysis: Dict[str, Any]
    critique: Dict[str, Any]
    final_report: str
    report_metadata: Dict[str, Any]
    
    # Observability & Diagnostics
    agent_history: List[AgentExecutionRecord]
    errors: List[Dict[str, Any]]
```

### Advantages of Explicit Shared State
1. **Type Safety & Serialization:** Automatically validates data formats using Pydantic V2 and serializes cleanly to JSON for REST/SSE endpoints.
2. **Deterministic State Inspection:** Allows the frontend or developers to view the complete internal state tree at any point via the State Inspector.
3. **Decoupled Contracts:** Agents only read the specific slices of state they need and write back to designated output keys.

---

## 5. Agent Communication

Communication in this architecture follows the **Blackboard Architectural Pattern**.

Agents do **not** invoke one another directly. Instead:
- Stage $N$ writes its output to `ResearchState`.
- Stage $N+1$ reads the accumulated state from `ResearchState`.

```
Coordinator ──> [Research Agent] ──commits findings──> [ ResearchState ]
                                                              │
Coordinator ──> [ Analyzer ]     <──reads findings────────────┘
                     │
                     └──commits themes─────────────────> [ ResearchState ]
                                                              │
Coordinator ──> [ Critic ]       <──reads findings+themes──────┘
                     │
                     └──commits critique───────────────> [ ResearchState ]
                                                              │
Coordinator ──> [ Writer ]       <──reads all artifacts───────┘
                     │
                     └──commits final report───────────> [ ResearchState ]
```

Each stage also appends an [`AgentExecutionRecord`](file:///D:/Linkific_Intern/Day%2022/backend/app/state/research_state.py) documenting:
- `agent`: Agent title
- `start_time` / `end_time`: ISO timestamps
- `duration_seconds`: High-precision float
- `status`: "completed" | "failed"
- `input_summary`: Human-readable summary of data consumed
- `output_summary`: Human-readable summary of artifacts produced
- `error_information`: Error trace if failure occurred

---

## 6. Workflow Planning

Workflow planning is handled deterministically by [`WorkflowPlanner`](file:///D:/Linkific_Intern/Day%2022/backend/app/workflow/planner.py):

1. **Declarative Stage Catalog:** Registers each stage's inputs, outputs, prerequisites, and conditional status.
2. **Linear Baseline Plan:** Standard execution plan:
   $$\text{research} \longrightarrow \text{analyze} \longrightarrow \text{criticize} \longrightarrow \text{write}$$
3. **Dynamic Refinement Branch:** If `Critic` sets `needs_refinement = True`, the plan expands:
   $$\text{criticize} \longrightarrow \text{research (refinement)} \longrightarrow \text{analyze (refinement)} \longrightarrow \text{criticize} \longrightarrow \text{write}$$

---

## 7. Error Handling

Failures are addressed systematically at two levels:

1. **Agent Level:** If an agent encounters an internal exception (e.g. data missing from state), the agent catches it, populates `state.errors`, writes a failed `AgentExecutionRecord`, and re-raises the error to the Coordinator.
2. **Coordinator Level:** The Coordinator wraps each stage in `_execute_stage_with_retry()`. If all retry attempts are exhausted, the workflow status is set to `"failed"`, the error is recorded, and execution terminates safely without emitting an invalid report.

---

## 8. Retry Mechanism

The Coordinator features an automated retry policy for transient operational faults:

```python
async def _execute_stage_with_retry(self, agent, stage_name, state, step_index, notify):
    for attempt in range(1, self.max_retries + 1):
        try:
            return await agent.execute(state, step_index=step_index)
        except Exception as exc:
            if attempt < self.max_retries:
                await asyncio.sleep(0.5 * attempt)  # Backoff
            else:
                notify(f"{agent.name} exhausted all retries.")
                raise exc
```

This prevents transient network interruptions, rate-limit blips, or socket timeouts from crashing the entire research session.

---

## 9. Data Flow

```
[User Query]
    │
    ▼
[Coordinator.run_workflow]
    │
    ├─> Initial State created: { query: "...", status: "running" }
    │
    ├─> Stage 1 (Research): Gathers 3-5 empirical findings & source citations
    │     State += { research_findings: [...], sources: [...] }
    │
    ├─> Stage 2 (Analyzer): Synthesizes findings into 3 themes & facts/assumptions
    │     State += { analysis: { themes: [...], fact_vs_assumptions: {...} } }
    │
    ├─> Stage 3 (Critic): Evaluates empirical rigor and assigns score (e.g. 8.8/10.0)
    │     State += { critique: { quality_score: 8.8, passes_validation: true, ... } }
    │
    ├─> [Refinement Check]: If score < 7.5 -> Refine; else proceed to Writer
    │
    ├─> Stage 4 (Writer): Merges all state components into structured Markdown report
    │     State += { final_report: "# Executive Research...", report_metadata: {...} }
    │
    └─> Final State returned: { status: "completed", final_report: "...", ... }
```

---

## 10. Technology Choices

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.12) | Asynchronous native ASGI, automatic OpenAPI documentation, clean dependency injection, high throughput. |
| **Data Validation** | Pydantic V2 | High-performance C-based validation (`pydantic-core`), strict type safety, automatic JSON serialization. |
| **HTTP Client** | HTTPX | Fully asynchronous HTTP client for external LLM API connectivity and integration testing via `ASGITransport`. |
| **Frontend Framework**| React 18 + Vite | Lightning-fast HMR builds, component-driven UI, zero build bloat, native ES module support. |
| **Icons & UI** | Lucide React | Modern, consistent iconography for all agent roles and workflow stages. |
| **Testing** | Pytest + pytest-asyncio | Standard in Python asynchronous testing with robust fixture support and test isolation. |

---

## 11. Project Structure

```
Day 22/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI routes, CORS, REST & SSE endpoints
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py           # Abstract BaseAgent with telemetry & logging
│   │   │   ├── coordinator.py          # Workflow planner, retry manager, refinement loop
│   │   │   ├── research_agent.py       # Empirical fact finder & source cataloger
│   │   │   ├── analyzer.py             # Thematic breakdown & fact vs assumption
│   │   │   ├── critic.py               # Peer reviewer, quality scorer, refinement signal
│   │   │   └── writer.py               # Executive Markdown report synthesizer
│   │   ├── state/
│   │   │   ├── __init__.py
│   │   │   └── research_state.py       # Explicit Shared State models & history records
│   │   ├── workflow/
│   │   │   ├── __init__.py
│   │   │   ├── planner.py              # Declarative workflow stages & sequence planner
│   │   │   └── engine.py               # Workflow runtime engine & SSE stream manager
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── llm_service.py          # Real LLM API caller & realistic mock engine
│   │   └── models/
│   │       ├── __init__.py
│   │       └── api_models.py           # Request & Response Pydantic DTOs
│   ├── tests/
│   │   ├── test_state.py               # Shared state unit tests
│   │   ├── test_research_agent.py      # Research agent unit tests
│   │   ├── test_analyzer.py            # Analyzer agent unit tests
│   │   ├── test_critic.py              # Critic agent unit tests
│   │   ├── test_writer.py              # Writer agent unit tests
│   │   ├── test_coordinator.py         # Coordinator orchestration & retry tests
│   │   ├── test_communication.py       # Agent communication & telemetry tests
│   │   └── test_e2e_workflow.py        # End-to-end API integration tests
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx              # System status & provider badges
│   │   │   ├── TopicInput.jsx          # Query input & preset topics
│   │   │   ├── WorkflowProgress.jsx    # Visual pipeline stepper
│   │   │   ├── AgentActivity.jsx       # Real-time agent activity & audit cards
│   │   │   ├── ReportViewer.jsx        # Markdown report renderer with export/copy
│   │   │   └── StateInspectorModal.jsx # Live Shared State JSON inspector
│   │   ├── services/
│   │   │   └── api.js                  # Frontend API client
│   │   ├── App.jsx                     # Top-level state and layout
│   │   ├── main.jsx                    # Vite React mount
│   │   └── index.css                   # Polished dark UI styles & typography
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
├── docs/
│   ├── responsibility-matrix.md        # Comprehensive 5-agent role matrix
│   ├── workflow.md                     # Mermaid workflow & sequence diagrams
│   ├── architecture.md                 # System architecture notes (this document)
│   └── demo.md                         # Demonstration guide & sample executions
├── pytest.ini
├── .gitignore
└── README.md
```

---

## 12. How to Run the Application

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ (tested on Node v24)
- npm

### Step 1: Start Backend Server
```powershell
cd "D:\Linkific_Intern\Day 22\backend"
# If virtual environment is not already active:
.\venv\Scripts\Activate.ps1
# Launch FastAPI server on port 8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Start Frontend Application
In a separate terminal:
```powershell
cd "D:\Linkific_Intern\Day 22\frontend"
npm run dev
```
Open your browser at `http://localhost:5173`.

### Step 3: Run Automated Test Suite
```powershell
cd "D:\Linkific_Intern\Day 22"
.\backend\venv\Scripts\pytest -v backend\tests
```

---

## 13. Example Execution Walkthrough

**Topic:** *"Impact of generative AI on software development"*

1. **User Submission:** User enters query on frontend and clicks **Start Research**.
2. **Coordinator Initialized:** Coordinator creates `wf_a1b2c3d4` and plans sequence: `["research", "analyze", "criticize", "write"]`.
3. **Research Agent (0.01s):** Gathers 4 empirical findings across McKinsey (2023), GitHub Research, and IEEE S&P (2024), extracting velocity metrics and security risks.
4. **Analyzer (0.01s):** Structures findings into 3 themes: *Productivity Acceleration*, *Security & Governance Boundaries*, and *Agentic Architecture Paradigm*.
5. **Critic (0.01s):** Reviews findings and analysis, scoring `8.8 / 10.0`. Approves output with recommendations to address junior vs. senior developer disparities.
6. **Writer (0.01s):** Compiles an executive 6-section research report with formal citations and strategic recommendations.
7. **Delivery:** The UI displays the completed report, metrics, and execution history.

---

## 14. Design Trade-offs

| Decision | Selected Approach | Alternative Considered | Rationale |
| :--- | :--- | :--- | :--- |
| **Agent State Topology** | Centralized Shared State (Blackboard) | Direct Peer-to-Peer Agent Messaging | Simplifies auditing, guarantees type safety, enables global time-travel inspection, and eliminates complex mesh routing. |
| **LLM Service Provider** | Dual Real LLM + Realistic Mock Engine | Real LLM Only | Guarantees 100% reliable execution out-of-the-box in local/offline test environments without billing or credential blockers, while supporting plug-and-play real LLM calls when keys are provided. |
| **Frontend Communication** | REST with Step Transition Emulation & SSE capability | WebSockets | HTTP REST + SSE is simpler, stateless, proxy-friendly, and has fewer reconnection edge cases. |

---

## 15. Future Improvements

1. **Live Web Crawling Integration:** Equip the Research Agent with search APIs (DuckDuckGo, Brave Search, or Tavily) for live indexing of breaking news.
2. **Multi-Model Routing:** Route different agents to different LLMs based on their strengths (e.g. Claude 3.5 Sonnet for Writer, GPT-4o for Analyzer, Gemini 1.5 Pro for Research).
3. **Persistent Vector Memory:** Store historic research reports in a local vector database (ChromaDB / Qdrant) so agents can perform cross-report comparative research.
4. **Human-in-the-Loop Approval:** Allow users to approve or alter Critic recommendations before the Writer synthesizes the final report.
