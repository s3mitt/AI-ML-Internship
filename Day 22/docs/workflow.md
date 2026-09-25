# Multi-Agent Workflow Specification

This document details the multi-agent execution pipeline, agent communication topologies, and decision branches implemented in the **Multi-Agent Research Assistant**.

---

## 1. Multi-Agent Workflow Diagram

```mermaid
flowchart TD
    classDef userNode fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef coordNode fill:#1e1b4b,stroke:#6366f1,stroke-width:2px,color:#fff;
    classDef agentNode fill:#0f172a,stroke:#38bdf8,stroke-width:1.5px,color:#fff;
    classDef stateNode fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef decisionNode fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#fff;
    classDef outputNode fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#fff;

    U["User Request / Query"]:::userNode --> C["Coordinator"]:::coordNode
    
    subgraph S1 ["Stage 1: Initialization & Planning"]
        C -->|"1. Initialize & Plan"| S[("Shared State (ResearchState)")]:::stateNode
    end

    subgraph S2 ["Stage 2: Information Gathering"]
        C -->|"2. Trigger Research"| R["Research Agent"]:::agentNode
        R -->|"Read Query / Context"| S
        R -->|"Write Findings, Sources, Notes"| S
    end

    subgraph S3 ["Stage 3: Thematic Analysis"]
        C -->|"3. Trigger Analysis"| A["Analyzer"]:::agentNode
        A -->|"Read Findings & Sources"| S
        A -->|"Write Themes, Fact/Assumption Map"| S
    end

    subgraph S4 ["Stage 4: Quality & Peer Critique"]
        C -->|"4. Trigger Critique"| CR["Critic"]:::agentNode
        CR -->|"Read Findings & Analysis"| S
        CR -->|"Write Quality Score & Feedback"| S
    end

    subgraph S5 ["Stage 5: Evaluation & Dynamic Routing"]
        S -->|"Read Critique Score"| DEC{"Score >= 7.5 ?"}:::decisionNode
        DEC -->|"No (Needs Refinement)"| REF["Refinement Directives"]:::decisionNode
        REF -->|"Re-run Research/Analysis"| C
        DEC -->|"Yes (Approved)"| W["Writer"]:::agentNode
    end

    subgraph S6 ["Stage 6: Synthesis & Delivery"]
        W -->|"Read All Validated State"| S
        W -->|"Write Final Markdown Report"| S
        S -->|"Deliver Verified State"| C
        C -->|"Return Final Response"| F["Final Research Report & Audit History"]:::outputNode
    end
```

---

## 2. Sequence Diagram: Agent-to-Agent Communication Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Client
    participant Coord as Coordinator
    participant State as Shared State
    participant Research as Research Agent
    participant Analyzer as Analyzer
    participant Critic as Critic
    participant Writer as Writer

    User->>Coord: POST /api/research { query }
    Coord->>State: Initialize ResearchState (workflow_plan, status="running")
    
    Coord->>Research: execute(state, step=1)
    Research->>State: Fetch query & preferences
    Research->>Research: Perform empirical fact & source gathering
    Research->>State: Commit research_findings, sources, notes
    Coord->>State: Record Research Agent telemetry to agent_history

    Coord->>Analyzer: execute(state, step=2)
    Analyzer->>State: Fetch research_findings & sources
    Analyzer->>Analyzer: Synthesize themes & isolate facts vs assumptions
    Analyzer->>State: Commit analysis object
    Coord->>State: Record Analyzer telemetry to agent_history

    Coord->>Critic: execute(state, step=3)
    Critic->>State: Fetch findings & analysis
    Critic->>Critic: Perform peer review & score quality (0-10)
    Critic->>State: Commit critique object (score, issues, recommendations)
    Coord->>State: Record Critic telemetry to agent_history

    alt Quality Score < 7.5 and iterations < max_refinements
        Coord->>Coord: Inspect critique.needs_refinement == True
        Coord->>Research: execute(state, step=4, refinement=True)
        Research->>State: Append verified refinement findings
        Coord->>Analyzer: execute(state, step=5, refinement=True)
        Analyzer->>State: Update analysis themes
        Coord->>Critic: execute(state, step=6)
        Critic->>State: Commit updated critique
    end

    Coord->>Writer: execute(state, step=N)
    Writer->>State: Fetch findings, sources, analysis, critique
    Writer->>Writer: Synthesize executive markdown report with citations
    Writer->>State: Commit final_report & report_metadata
    Coord->>State: Record Writer telemetry to agent_history

    Coord->>State: Mark workflow_status = "completed"
    Coord->>State: Record Coordinator summary to agent_history
    Coord-->>User: Return complete ResearchResponse DTO
```

---

## 3. Communication Flow Mechanics

### Indirect Communication via Central Shared State
Unlike peer-to-peer point-to-point architectures where agents pass arbitrary payload arguments directly, our system adheres to **Blackboard / Shared State Pattern**:
1. **Zero Point-to-Point Couplings:** The `Analyzer` does not call `Research Agent`. It only inspects the `research_findings` array committed to `ResearchState`.
2. **Schema Invariant:** Every stage reads typed sub-structures defined via Pydantic models (`Finding`, `SourceReference`, `AnalysisTheme`, `CriticEvaluation`).
3. **Auditability:** Because every mutation passes through `ResearchState`, the complete trajectory is preserved in `state.agent_history`.

### The Refinement Feedback Loop
1. When the `Critic` executes, it evaluates the empirical rigor of the findings and the coherence of the analysis.
2. If gaps are identified (or if quality falls below threshold `7.5`), `state.critique.needs_refinement` is set to `True`.
3. The `Coordinator` inspects this flag. If the refinement budget (`max_refinements = 1`) is not exceeded, the Coordinator routes control back to the target stage with explicit instructions from `state.critique.recommendations`.
4. Once refined findings are cataloged and re-analyzed, the Critic re-evaluates the output before report generation proceeds. This prevents low-quality hallucinations or incomplete studies from reaching the final deliverable.
