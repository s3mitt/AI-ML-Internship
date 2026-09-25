# Multi-Agent Responsibility Matrix

This document defines the formal operational boundaries, interfaces, dependencies, and state-mutation privileges for every agent in the **Multi-Agent Research Assistant** system.

---

## 1. Comprehensive Agent Responsibility Matrix

| Agent | Core Role | Primary Inputs | Outputs Produced | Upstream Dependencies | Communicates With | Shared State Fields Read | Shared State Fields Written |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Coordinator** | Entry point, workflow planner, stage supervisor, retry coordinator, refinement director | User research query, research preferences | Initialized state, workflow plan, execution records, final response | None (Root orchestrator) | All agents (`Research Agent`, `Analyzer`, `Critic`, `Writer`) | `query`, `preferences`, `critique`, `workflow_plan`, `errors` | `workflow_id`, `workflow_status`, `workflow_plan`, `current_step`, `agent_history`, `errors`, `refinement_iterations` |
| **Research Agent** | Empirical evidence gathering, fact extraction, academic/industry source cataloging | Research topic, query preferences, critic refinement directives (if iterative) | Verified findings list, primary sources, research coverage notes | Coordinator, search/LLM knowledge provider | Coordinator → Shared State | `query`, `preferences`, `critique` *(on refinement)*, `refinement_iterations` | `research_findings`, `sources`, `research_notes`, `agent_history` |
| **Analyzer** | Thematic synthesis, pattern recognition, fact vs. assumption demarcation | Research findings, source reference catalog | Synthesized themes, categorized facts/assumptions, structured insights | Research Agent | Research Agent → Analyzer → Shared State | `query`, `research_findings`, `sources` | `analysis` (themes, verified facts, unverified assumptions, strategic insights), `agent_history` |
| **Critic** | Peer review, claim validation, bias auditing, quality scoring, refinement signaling | Empirical findings, thematic analysis | Quantitative quality score (0-10), issues list, missing angles, recommendations, refinement trigger | Research Agent, Analyzer | Analyzer → Critic → Shared State (and loops to Coordinator if refinement required) | `query`, `research_findings`, `analysis`, `refinement_iterations` | `critique` (`quality_score`, `passes_validation`, `needs_refinement`, `target_refinement_stage`, `identified_issues`, `missing_information`, `recommendations`, `bias_assessment`), `agent_history` |
| **Writer** | Executive document synthesis, citation linking, critic feedback incorporation | Validated research findings, analyzed themes, critic evaluations | Publication-grade Markdown report, report metadata (word count, sources cited) | Research Agent, Analyzer, Critic | Critic → Writer → Coordinator | `query`, `research_findings`, `sources`, `analysis`, `critique` | `final_report`, `report_metadata`, `agent_history` |

---

## 2. Dedicated Coordinator Responsibilities

The **Coordinator** functions as the central operating system kernel of the multi-agent architecture. Its responsibilities are explicitly decoupled from domain data extraction:

### A. Lifecycle Management & State Initialization
- Acts as the single point of entry for user requests.
- Generates a unique `workflow_id` (`wf_<uuid>`).
- Instantiates the typed `ResearchState` container with baseline schemas.
- Configures operational limits (e.g., `max_retries = 2`, `max_refinements = 1`).

### B. Dynamic Workflow Planning
- Evaluates the query domain and user preferences to construct an ordered stage sequence (`workflow_plan`).
- Baseline plan: `["research", "analyze", "criticize", "write"]`.
- Tracks transition states: `initialized` → `running` → `completed` (or `failed`).

### C. State Passing & Interface Isolation
- Passes the central `ResearchState` reference between agents.
- Ensures agents never invoke one another directly through tightly coupled function calls; all inputs are derived from prior states, and all outputs are committed back to `ResearchState`.

### D. Refinement Loop Supervision
- Inspects the Critic's verdict after the critique stage.
- If `needs_refinement == True` and `refinement_iterations < max_refinements`:
  - Dynamically routes control back to the designated `target_refinement_stage` (`research` or `analyzer`).
  - Instructs the agent to perform targeted verification addressing `critique.recommendations`.
  - Re-executes the Critic stage to confirm resolution before advancing to synthesis.

### E. Fault Tolerance & Retry Strategy
- Implements exponential or incremental backoff retries on transient errors (network drops, rate limits).
- Logs structured error telemetry (`state.add_error()`) without producing corrupted or silent incomplete outputs.
- Marks `workflow_status = "failed"` if terminal failures persist.

---

## 3. Separation of Concerns Principles

1. **Research Agent does not analyze:** It limits its scope to finding verifiable empirical claims and linking primary sources.
2. **Analyzer does not judge validity:** It synthesizes patterns and structures facts vs. assumptions without rejecting claims.
3. **Critic does not write the report:** It acts purely as an adversarial reviewer and scoring authority.
4. **Writer does not invent findings:** It is constrained to synthesize only the validated findings present in `state.research_findings` and explicitly address items from `state.critique`.
5. **Coordinator does not synthesize content:** It focuses strictly on workflow planning, timing telemetry, error management, and routing.
