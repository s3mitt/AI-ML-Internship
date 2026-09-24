"""Business logic and service layer for item processing.

This module provides the core processing logic for both synchronous and
asynchronous execution flows, demonstrating the critical differences between
blocking I/O (time.sleep) and non-blocking cooperative multitasking (asyncio.sleep).
"""

import asyncio
from datetime import datetime, timezone
import logging
import os
from pathlib import Path
import time
import uuid

from app.models.schemas import ItemCreate, ItemResponse

logger = logging.getLogger("app.services.item_service")

# Base directory for logs
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG_FILE = LOG_DIR / "background_tasks.log"

# Default simulated I/O delay in seconds (can be overridden via environment)
# NOTE: This delay simulates an external database or network call.
SIMULATED_IO_DELAY = float(os.getenv("SIMULATED_IO_DELAY", "0.05"))


class ItemService:
    """Service class handling item calculations, storage simulations,

    and audit trail logging.
    """

    def __init__(self, io_delay: float = SIMULATED_IO_DELAY):
        self.io_delay = io_delay

    def process_item_sync(self, item: ItemCreate, client_ip: str = "unknown") -> ItemResponse:
        """Processes an item using SYNCHRONOUS, BLOCKING I/O.

        IMPORTANT BENCHMARK NOTE:
        We use `time.sleep()` strictly to simulate a blocking I/O operation
        (e.g., legacy synchronous database query, disk write, or external HTTP call).
        FastAPI executes standard `def` routes inside an external threadpool worker.
        When many concurrent requests arrive, threadpool exhaustion and context
        switching overhead limit throughput.
        """
        # Simulate blocking I/O (database query / network latency)
        time.sleep(self.io_delay)

        item_id = str(uuid.uuid4())
        total = round(item.quantity * item.price, 2)
        now_iso = datetime.now(timezone.utc).isoformat()

        logger.info(
            f"[SYNC] Processed item {item.name} (id={item_id}) for client={client_ip}"
        )

        return ItemResponse(
            id=item_id,
            name=item.name,
            quantity=item.quantity,
            price=item.price,
            total_price=total,
            status="completed",
            processing_type="sync",
            processed_at=now_iso,
            message=f"Item '{item.name}' processed successfully via synchronous pipeline.",
        )

    async def process_item_async(
        self, item: ItemCreate, client_ip: str = "unknown"
    ) -> ItemResponse:
        """Processes an item using ASYNCHRONOUS, NON-BLOCKING I/O.

        IMPORTANT BENCHMARK NOTE:
        We use `await asyncio.sleep()` to yield control back to the event loop.
        While this task waits for simulated I/O, the single Python event loop
        can immediately switch to process other incoming concurrent requests
        without spawning OS threads or incurring heavy context switching overhead.
        """
        # Non-blocking cooperative yield to the event loop
        await asyncio.sleep(self.io_delay)

        item_id = str(uuid.uuid4())
        total = round(item.quantity * item.price, 2)
        now_iso = datetime.now(timezone.utc).isoformat()

        logger.info(
            f"[ASYNC] Processed item {item.name} (id={item_id}) for client={client_ip}"
        )

        return ItemResponse(
            id=item_id,
            name=item.name,
            quantity=item.quantity,
            price=item.price,
            total_price=total,
            status="completed",
            processing_type="async",
            processed_at=now_iso,
            message=f"Item '{item.name}' processed successfully via asynchronous pipeline.",
        )

    @staticmethod
    def log_background_audit(
        item_id: str,
        item_name: str,
        processing_type: str,
        client_ip: str = "unknown",
    ) -> None:
        """Background job to record an audit trail entry.

        WHY SUITABLE FOR BACKGROUND TASKS:
        Writing telemetry, analytics, or audit records is non-critical to the
        immediate client response. By executing this as a FastAPI `BackgroundTask`,
        the HTTP response is dispatched immediately to the client without waiting
        for disk write or remote telemetry latency.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        audit_entry = (
            f"[{timestamp}] AUDIT_EVENT | id={item_id} | name={item_name} | "
            f"type={processing_type} | client_ip={client_ip} | status=AUDIT_RECORDED\n"
        )
        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(audit_entry)
            logger.info(f"[BACKGROUND_TASK] Audit entry written for item {item_id}")
        except Exception as exc:
            logger.error(f"[BACKGROUND_TASK] Failed to write audit log: {exc}")
