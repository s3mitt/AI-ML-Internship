# Multi-Agent Research Assistant - Demonstration Guide

This guide provides step-by-step instructions for demonstrating and verifying the **Multi-Agent Research Assistant** locally.

---

## 1. Quick Verification Checklist

- [x] Backend running on `http://localhost:8000`
- [x] Frontend running on `http://localhost:5173`
- [x] All 5 required agents execute in sequence: Coordinator → Research Agent → Analyzer → Critic → Writer
- [x] Explicit Shared State passes through every stage
- [x] Observability metadata logged in `agent_history`
- [x] Final research report generated in publication-grade Markdown
- [x] Automated test suite passes (20/20 tests)

---

## 2. Running Automated Tests

Run the comprehensive pytest suite:

```powershell
cd "D:\Linkific_Intern\Day 22"
.\backend\venv\Scripts\pytest -v backend\tests
```

**Expected Result:**
```
backend/tests/test_analyzer.py::test_analyzer_empty_state_guardrail PASSED
backend/tests/test_analyzer.py::test_analyzer_synthesizes_themes_and_facts PASSED
backend/tests/test_communication.py::test_agent_communication_and_observability PASSED
backend/tests/test_coordinator.py::test_coordinator_initializes_state_and_plan PASSED
backend/tests/test_coordinator.py::test_coordinator_full_execution_flow PASSED
backend/tests/test_coordinator.py::test_coordinator_retry_mechanism_on_transient_failure PASSED
backend/tests/test_coordinator.py::test_coordinator_handles_unrecoverable_failure PASSED
backend/tests/test_critic.py::test_critic_requires_findings_and_analysis PASSED
backend/tests/test_critic.py::test_critic_produces_quality_score_and_critique PASSED
backend/tests/test_critic.py::test_critic_refinement_trigger_when_threshold_unmet PASSED
backend/tests/test_e2e_workflow.py::test_api_health_and_info PASSED
backend/tests/test_e2e_workflow.py::test_api_end_to_end_research PASSED
backend/tests/test_research_agent.py::test_research_agent_execution PASSED
backend/tests/test_research_agent.py::test_research_agent_refinement PASSED
backend/tests/test_state.py::test_shared_state_initialization PASSED
backend/tests/test_state.py::test_shared_state_history_recording PASSED
backend/tests/test_state.py::test_shared_state_error_recording PASSED
backend/tests/test_state.py::test_shared_state_lookups_and_summary PASSED
backend/tests/test_writer.py::test_writer_guardrails PASSED
backend/tests/test_writer.py::test_writer_generates_markdown_report_with_metadata PASSED
============================== 20 passed in ~1.0s ==============================
```

---

## 3. Testing Backend via cURL / PowerShell

### Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
```

### System Info
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/system/info" -Method Get
```

### Run Multi-Agent Research Workflow
```powershell
$body = @{
    query = "Impact of generative AI on software development"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/research" -Method Post -Body $body -ContentType "application/json"
$response | Select-Object -Property workflow_id, status, query
```

---

## 4. Demonstrating the Web User Interface

1. Start both backend and frontend.
2. Open `http://localhost:5173` in any browser.
3. Observe the header showing:
   - **Deterministic Mock Engine** badge (or **LLM: OPENAI / GEMINI** if API key is set)
   - **5 Specialized Agents** badge
4. Click one of the quick sample queries:
   - *"Impact of generative AI on software development"*
5. Click **Start Research**.
6. Observe:
   - The **Workflow Execution Pipeline** steps animate:
     - `✓ Coordinator`
     - `✓ Research Agent`
     - `✓ Analyzer`
     - `✓ Critic`
     - `→ Writer`
   - The **Agent Activity & Execution Audit Log** displays cards for each agent with durations, input summaries, and output summaries.
   - Click to expand any agent card to see:
     - Research findings & citations
     - Analysis themes and facts vs. assumptions
     - Critic quality score (e.g. 8.8 / 10.0) and recommendations
     - Writer word count and metadata
   - The **Final Research Report** renders in formatted Markdown with executive summary, empirical findings, comparative tables, and full references.
   - Click **Export (.md)** to download the report file.
   - Click **Shared State Inspector** in the top right to view the live JSON state tree.
