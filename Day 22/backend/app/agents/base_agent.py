"""Base Agent Abstract Class for Multi-Agent Workflow.

Ensures unified error tracking, execution timing, input/output summarization,
and strict shared-state mutation adherence.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging
import time
from typing import Optional

from ..state.research_state import AgentExecutionRecord, ResearchState

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract Base Class for all specialized AI agents."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    @abstractmethod
    async def _process(self, state: ResearchState) -> ResearchState:
        """Internal agent execution logic to be implemented by child agents."""
        pass

    async def execute(self, state: ResearchState, step_index: int = 0) -> ResearchState:
        """Standardized lifecycle runner: records telemetry, executes, and logs history."""
        start_time_dt = datetime.now(timezone.utc)
        start_time_str = start_time_dt.isoformat()
        t0 = time.perf_counter()

        input_summary = self._summarize_input(state)
        logger.info(f"[{self.name}] Starting execution. Step: {step_index}")

        try:
            state = await self._process(state)
            duration = round(time.perf_counter() - t0, 3)
            end_time_str = datetime.now(timezone.utc).isoformat()
            output_summary = self._summarize_output(state)

            record = AgentExecutionRecord(
                agent=self.name,
                start_time=start_time_str,
                end_time=end_time_str,
                duration_seconds=duration,
                status="completed",
                input_summary=input_summary,
                output_summary=output_summary,
                step_index=step_index,
                iteration=state.refinement_iterations + 1,
            )
            state.add_history(record)
            logger.info(f"[{self.name}] Finished successfully in {duration}s")
            return state

        except Exception as exc:
            duration = round(time.perf_counter() - t0, 3)
            end_time_str = datetime.now(timezone.utc).isoformat()
            error_msg = f"{type(exc).__name__}: {str(exc)}"
            logger.error(f"[{self.name}] Execution failed: {error_msg}")

            record = AgentExecutionRecord(
                agent=self.name,
                start_time=start_time_str,
                end_time=end_time_str,
                duration_seconds=duration,
                status="failed",
                input_summary=input_summary,
                output_summary="Failed to complete task.",
                error_information=error_msg,
                step_index=step_index,
                iteration=state.refinement_iterations + 1,
            )
            state.add_history(record)
            state.add_error(agent=self.name, error_message=error_msg, error_type=type(exc).__name__)
            raise exc

    @abstractmethod
    def _summarize_input(self, state: ResearchState) -> str:
        """Returns concise description of inputs consumed by this agent."""
        pass

    @abstractmethod
    def _summarize_output(self, state: ResearchState) -> str:
        """Returns concise description of outputs produced by this agent."""
        pass
