"""Request timing and diagnostics middleware.

This module intercepts every incoming HTTP request, records start/end timestamps,
appends the processing duration to custom response headers (`X-Process-Time`),
and logs structured execution telemetry.
"""

import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Configure logger for middleware telemetry
logger = logging.getLogger("app.middleware.timing")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class TimingMiddleware(BaseHTTPMiddleware):
    """Measures total request processing time for every endpoint.

    Workflow:
    1. Intercept incoming request and record start time using high-precision `time.perf_counter()`.
    2. Pass control down the middleware/route pipeline asynchronously via `await call_next(request)`.
    3. Calculate the elapsed processing time once the downstream handler returns.
    4. Inject `X-Process-Time` (in seconds) into response headers.
    5. Output structured access log: `<METHOD> <PATH> - <STATUS> - <TIME>s`.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()

        # Process the request through downstream routes and middleware
        response = await call_next(request)

        # Calculate duration in seconds
        process_time = time.perf_counter() - start_time

        # Inject diagnostic header into the response
        response.headers["X-Process-Time"] = f"{process_time:.6f}"

        # Structured diagnostic log
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
        )

        return response
