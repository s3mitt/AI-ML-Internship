# ==============================================================================
# Production Multi-Stage Dockerfile
# Optimizes image size, layer caching, security hardening, and non-root execution.
# ==============================================================================

# Stage 1: Build stage
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install --no-warn-script-location -r requirements.txt


# Stage 2: Final Runtime Stage
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/app:/install/lib/python3.12/site-packages" \
    APP_ENV="production" \
    PORT=8000 \
    HOST="0.0.0.0"

# Copy installed Python packages from builder stage
COPY --from=builder /install /install

# Create non-root system user and group for security
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser && \
    chown -R appuser:appgroup /app

# Copy application source code
COPY --chown=appuser:appgroup ./app /app/app
COPY --chown=appuser:appgroup pytest.ini /app/pytest.ini

# Switch to non-privileged user
USER appuser

# Expose HTTP port
EXPOSE 8000

# Container healthcheck using standard library urllib
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live').read()" || exit 1

# Start production server using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
