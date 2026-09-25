"""Workflow Engine managing multi-agent execution, state persistence, and event streaming."""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone
import json
import logging
from typing import Any, AsyncGenerator, Callable, Dict, Optional

from ..agents.coordinator import Coordinator
from ..state.research_state import ResearchState

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Manages active and historical research workflows, event queues, and execution."""

    def __init__(self):
        self.coordinator = Coordinator()
        self._states: Dict[str, ResearchState] = {}
        self._event_queues: Dict[str, asyncio.Queue] = {}

    def get_state(self, workflow_id: str) -> Optional[ResearchState]:
        return self._states.get(workflow_id)

    def list_workflows(self) -> Dict[str, Any]:
        return {
            wid: state.to_summary_dict()
            for wid, state in self._states.items()
        }

    async def execute_sync(
        self, query: str, preferences: Optional[dict] = None
    ) -> ResearchState:
        """Executes workflow synchronously and caches result."""
        state = self.coordinator.initialize_state(query, preferences)
        self._states[state.workflow_id] = state
        final_state = await self.coordinator.execute_workflow(state)
        self._states[final_state.workflow_id] = final_state
        return final_state

    async def execute_streaming(
        self, query: str, preferences: Optional[dict] = None
    ) -> AsyncGenerator[str, None]:
        """Executes workflow asynchronously while streaming Server-Sent Events (SSE)."""
        state = self.coordinator.initialize_state(query, preferences)
        workflow_id = state.workflow_id
        self._states[workflow_id] = state

        queue: asyncio.Queue = asyncio.Queue()
        self._event_queues[workflow_id] = queue

        def on_progress(updated_state: ResearchState, message: str):
            event_payload = {
                "event": "progress",
                "workflow_id": workflow_id,
                "current_step": updated_state.current_step,
                "workflow_status": updated_state.workflow_status,
                "message": message,
                "history_length": len(updated_state.agent_history),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "state_summary": updated_state.to_summary_dict(),
            }
            try:
                queue.put_nowait(event_payload)
            except Exception as q_err:
                logger.warning(f"Failed to queue event: {q_err}")

        # Launch execution task
        async def runner():
            try:
                final_state = await self.coordinator.execute_workflow(
                    state, progress_callback=on_progress
                )
                self._states[workflow_id] = final_state
                await queue.put({
                    "event": "completed",
                    "workflow_id": workflow_id,
                    "workflow_status": final_state.workflow_status,
                    "final_state": final_state.model_dump(),
                })
            except Exception as err:
                logger.error(f"Streaming runner error: {err}")
                await queue.put({
                    "event": "error",
                    "workflow_id": workflow_id,
                    "workflow_status": "failed",
                    "error": str(err),
                })
            finally:
                await queue.put(None)  # Signal termination

        asyncio.create_task(runner())

        # Yield events from queue as SSE formatted text
        while True:
            item = await queue.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

        if workflow_id in self._event_queues:
            del self._event_queues[workflow_id]


# Global workflow engine instance
_workflow_engine: Optional[WorkflowEngine] = None

def get_workflow_engine() -> WorkflowEngine:
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine
