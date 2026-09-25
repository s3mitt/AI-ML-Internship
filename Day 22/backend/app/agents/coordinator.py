"""Coordinator Agent Implementation.

Role:
- Master orchestrator and central entry point for the Multi-Agent Research Assistant.
- Initializes and manages the explicit Shared State.
- Dynamically creates and tracks the workflow plan.
- Dispatches execution to specialized agents: Research Agent -> Analyzer -> Critic -> Writer.
- Evaluates Critic findings: if critique scores low and indicates refinement, routes
  execution back to the target refinement stage.
- Implements robust error recovery and retry logic to prevent silent invalid state.
- Exposes real-time event hooks for streaming UI telemetry.
"""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone
import logging
from typing import Any, Callable, Dict, List, Optional

from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .analyzer import Analyzer
from .critic import Critic
from .writer import Writer
from ..state.research_state import AgentExecutionRecord, ResearchState

logger = logging.getLogger(__name__)


class Coordinator(BaseAgent):
    """The master workflow coordinator and orchestrator."""

    def __init__(self, max_retries: int = 2, max_refinements: int = 1):
        super().__init__(
            name="Coordinator",
            role="Workflow Planning, Stage Orchestration, Refinement Routing, and Shared State Governance",
        )
        self.max_retries = max_retries
        self.max_refinements = max_refinements

        # Initialize sub-agents
        self.research_agent = ResearchAgent()
        self.analyzer_agent = Analyzer()
        self.critic_agent = Critic()
        self.writer_agent = Writer()

    def initialize_state(self, query: str, preferences: Optional[Dict[str, Any]] = None) -> ResearchState:
        """Initializes a clean, explicit Shared State object for a research query."""
        plan = self.plan_workflow(query, preferences or {})
        state = ResearchState(
            query=query.strip(),
            preferences=preferences or {},
            workflow_plan=plan,
            workflow_status="initialized",
            max_refinements=self.max_refinements,
        )
        return state

    def plan_workflow(self, query: str, preferences: Dict[str, Any]) -> List[str]:
        """Creates the initial step sequence plan."""
        # Standard sequential baseline with conditional loop
        plan = ["research", "analyze", "criticize", "write"]
        logger.info(f"Planned workflow for '{query}': {plan}")
        return plan

    async def run_workflow(
        self,
        query: str,
        preferences: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[ResearchState, str], None]] = None,
    ) -> ResearchState:
        """Executes the complete multi-agent workflow from start to finish."""
        state = self.initialize_state(query, preferences)
        return await self.execute_workflow(state, progress_callback)

    async def execute_workflow(
        self,
        state: ResearchState,
        progress_callback: Optional[Callable[[ResearchState, str], None]] = None,
    ) -> ResearchState:
        """Runs the orchestrator loop against an initialized Shared State."""
        state.workflow_status = "running"
        coord_start = datetime.now(timezone.utc).isoformat()

        def notify(msg: str):
            logger.info(f"[Coordinator] {msg}")
            if progress_callback:
                try:
                    progress_callback(state, msg)
                except Exception as cb_err:
                    logger.warning(f"Progress callback error: {cb_err}")

        notify(f"Initialized research workflow {state.workflow_id} for query '{state.query}'")

        try:
            # 1. Execute Research Agent
            state = await self._execute_stage_with_retry(
                agent=self.research_agent,
                stage_name="research",
                state=state,
                step_index=1,
                notify=notify,
            )

            # 2. Execute Analyzer Agent
            state = await self._execute_stage_with_retry(
                agent=self.analyzer_agent,
                stage_name="analyze",
                state=state,
                step_index=2,
                notify=notify,
            )

            # 3. Execute Critic Agent
            state = await self._execute_stage_with_retry(
                agent=self.critic_agent,
                stage_name="criticize",
                state=state,
                step_index=3,
                notify=notify,
            )

            # 4. Refinement Loop Check: Does Critic request refinement?
            if state.critique.get("needs_refinement") and state.refinement_iterations < state.max_refinements:
                target_stage = state.critique.get("target_refinement_stage", "research")
                state.refinement_iterations += 1
                notify(f"Critic requested refinement on stage '{target_stage}'. Starting iteration {state.refinement_iterations}...")

                if target_stage == "research":
                    state = await self._execute_stage_with_retry(
                        agent=self.research_agent,
                        stage_name="research_refinement",
                        state=state,
                        step_index=4,
                        notify=notify,
                    )
                    state = await self._execute_stage_with_retry(
                        agent=self.analyzer_agent,
                        stage_name="analyze_refinement",
                        state=state,
                        step_index=5,
                        notify=notify,
                    )
                elif target_stage == "analyzer":
                    state = await self._execute_stage_with_retry(
                        agent=self.analyzer_agent,
                        stage_name="analyze_refinement",
                        state=state,
                        step_index=4,
                        notify=notify,
                    )

                # Re-evaluate with Critic after refinement
                state = await self._execute_stage_with_retry(
                    agent=self.critic_agent,
                    stage_name="criticize_post_refinement",
                    state=state,
                    step_index=6,
                    notify=notify,
                )

            # 5. Execute Writer Agent
            writer_step_idx = 4 + (3 if state.refinement_iterations > 0 else 0)
            state = await self._execute_stage_with_retry(
                agent=self.writer_agent,
                stage_name="write",
                state=state,
                step_index=writer_step_idx,
                notify=notify,
            )

            # Finalize workflow state
            state.workflow_status = "completed"
            state.current_step = None
            coord_end = datetime.now(timezone.utc).isoformat()

            # Record Coordinator execution summary
            coord_record = AgentExecutionRecord(
                agent=self.name,
                start_time=coord_start,
                end_time=coord_end,
                duration_seconds=round(
                    sum(rec.duration_seconds for rec in state.agent_history), 3
                ),
                status="completed",
                input_summary=f"Initiated workflow with query: '{state.query}'",
                output_summary=(
                    f"Workflow successfully orchestrated {len(state.agent_history)} agent operations. "
                    f"Final report generated ({len(state.final_report)} chars)."
                ),
                step_index=0,
                iteration=state.refinement_iterations + 1,
            )
            state.add_history(coord_record)
            notify("All workflow stages completed successfully.")
            return state

        except Exception as e:
            state.workflow_status = "failed"
            notify(f"Workflow encountered fatal error: {str(e)}")
            raise e

    async def _execute_stage_with_retry(
        self,
        agent: BaseAgent,
        stage_name: str,
        state: ResearchState,
        step_index: int,
        notify: Callable[[str], None],
    ) -> ResearchState:
        """Executes a single agent stage with configurable retries on transient errors."""
        state.current_step = stage_name
        notify(f"Executing {agent.name} (Stage: {stage_name})...")

        last_exception: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                state = await agent.execute(state, step_index=step_index)
                return state
            except Exception as exc:
                last_exception = exc
                logger.warning(
                    f"Stage '{stage_name}' failed attempt {attempt}/{self.max_retries}: {str(exc)}"
                )
                if attempt < self.max_retries:
                    notify(f"{agent.name} encountered error. Retrying attempt {attempt + 1}/{self.max_retries}...")
                    await asyncio.sleep(0.5 * attempt)
                else:
                    notify(f"{agent.name} exhausted all {self.max_retries} retries.")

        if last_exception:
            raise last_exception
        return state

    async def _process(self, state: ResearchState) -> ResearchState:
        return await self.execute_workflow(state)

    def _summarize_input(self, state: ResearchState) -> str:
        return f"User research query: '{state.query}'"

    def _summarize_output(self, state: ResearchState) -> str:
        return f"Completed full multi-agent lifecycle. Report generated: {bool(state.final_report)}"
