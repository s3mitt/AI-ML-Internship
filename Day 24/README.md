# Production-Ready Microservice Architecture
## Day 24 Internship Project — Testing, Logging, Docker, Environment Variables & Monitoring

A production-grade Python FastAPI microservice demonstrating enterprise best practices in automated testing with **Pytest**, structured **Logging** with correlation IDs, containerization with **Docker** and **Docker Compose**, **Environment Variable** management with **Pydantic Settings**, and real-time observability with **Prometheus Metrics** and hardware telemetry.

---

## 📋 Learning Objectives & Implementation Highlights

### 1. Pytest (Automated Testing)
- **Comprehensive Test Suite**: 51 passing tests (33 unit tests, 18 API integration tests) executed in **0.27s**.
- **Pytest Configuration (`pytest.ini`)**: Configured test discovery, strict markers (`unit`, `api`, `monitoring`), and clean terminal reporting.
- **Fixtures & Isolation (`conftest.py`)**: Session-scoped test client, automatic test state cleanup (`clean_task_service`), and mock environment patching.
- **End-to-End Workflow Testing**: Full lifecycle tests (Create $\rightarrow$ Pending $\rightarrow$ Execute $\rightarrow$ Completed $\rightarrow$ Delete $\rightarrow$ 404).

### 2. Structured Logging
- **JSON Formatting**: Production logs formatted as single-line JSON records using `python-json-logger`.
- **Request Correlation IDs**: Injected and propagated across async execution contexts using Python `contextvars` and custom `CorrelationIdFilter`.
- **Log Level Management**: Configurable log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) via environment variables.
- **PII & Secret Sanitization**: Credentials and tokens masked automatically with `pydantic.SecretStr`.

### 3. Docker Basics (Containerization)
- **Multi-Stage Build (`Dockerfile`)**: Builder stage compiles dependencies; minimal runtime stage uses `python:3.12-slim`.
- **Security Hardening**: Runs as unprivileged non-root user (`appuser:appgroup` UID `10001`).
- **Container Healthcheck**: Configured `HEALTHCHECK` polling the `/health/live` probe every 30s.
- **Multi-Service Composition (`docker-compose.yml`)**: Orchestrates the API service and Prometheus server on an isolated bridge network.
- **Clean Build Rules (`.dockerignore`)**: Excludes virtual environments, caches, git history, and secrets.

### 4. Environment Variables (12-Factor App)
- **Type-Safe Configuration (`app/config.py`)**: Uses `pydantic-settings` `BaseSettings` for automatic type casting and range validation.
- **Configuration Template (`.env.example`)**: Complete, documented environment variable template for deployments.
- **Multi-Environment Support**: Strict validation for `development`, `staging`, `production`, and `testing`.

### 5. Monitoring & Observability
- **Prometheus Metrics Endpoint (`/metrics`)**: Exposes scrapable metrics using `prometheus_client`.
- **Request Instrumentation**: Counter `http_requests_total`, histogram `http_request_duration_seconds`, and gauge `http_active_requests`.
- **Business Task Telemetry**: Counter `task_executions_total` tracking success and failure by task type.
- **Hardware Telemetry (`/api/v1/telemetry`)**: Real-time CPU, RAM, Disk, and process thread metrics via `psutil`.
- **Orchestration Probes**: `/health/live` (liveness) and `/health/ready` (readiness).

---

## 📁 Project Directory Structure

```
D:\Linkific_Intern\Day 24\
├── app/
│   ├── __init__.py                # Package initialization
│   ├── config.py                  # Pydantic BaseSettings & environment validation
│   ├── logging_config.py          # Structured JSON logging & correlation filter
│   ├── monitoring.py              # Prometheus metrics & system telemetry
│   ├── main.py                    # FastAPI application, middleware, lifecycle
│   ├── models/
│   │   ├── __init__.py            # Model exports
│   │   └── schemas.py             # Pydantic request & response schemas
│   ├── routers/
│   │   ├── __init__.py            # Router exports
│   │   ├── health.py              # Liveness & readiness probes (/health/live, /health/ready)
│   │   ├── metrics.py             # Prometheus metrics (/metrics) & telemetry
│   │   └── tasks.py               # Task management CRUD & execution endpoints
│   └── services/
│       ├── __init__.py            # Service exports
│       └── task_service.py        # Task domain operations, logging & telemetry
├── tests/
│   ├── __init__.py                # Test package initialization
│   ├── conftest.py                # Pytest fixtures, test client, mock data
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_config.py         # Config validation & secret masking tests
│   │   ├── test_logging.py        # JSON logging & correlation ID tests
│   │   ├── test_monitoring.py     # Prometheus metrics & telemetry tests
│   │   └── test_task_service.py   # Task service logic & error handling tests
│   └── api/
│       ├── __init__.py
│       ├── test_health_api.py     # Probes & health endpoint tests
│       ├── test_metrics_api.py    # /metrics scrape & telemetry tests
│       └── test_tasks_api.py      # Task API endpoints & lifecycle tests
├── Dockerfile                     # Multi-stage production container definition
├── docker-compose.yml             # Orchestration for API + Prometheus
├── prometheus.yml                 # Prometheus scrape configuration
├── .dockerignore                  # Docker build exclusions
├── .env.example                   # Environment configuration template
├── .env                           # Local environment configuration
├── pytest.ini                     # Pytest runner configuration
├── requirements.txt               # Pinned project dependencies
├── DEPLOYMENT_CHECKLIST.md        # Comprehensive deployment gate checklist
├── PRODUCTION_READINESS_REPORT.md # Production readiness audit & scorecard
└── README.md                      # Complete system documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.12+ installed
- Docker & Docker Compose (optional for containerized deployment)

### 2. Environment Setup
```bash
# Clone or navigate into the project directory
cd "D:\Linkific_Intern\Day 24"

# Create a virtual environment (optional)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install project dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and adjust as needed:
```bash
cp .env.example .env
```

### 4. Run the Service Locally
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The interactive documentation will be accessible at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Probe**: [http://localhost:8000/health/live](http://localhost:8000/health/live)
- **Prometheus Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

## 🧪 Running Automated Tests (Pytest)

The project includes 51 automated unit and API integration tests.

```bash
# Run the entire test suite with verbose output
pytest -v

# Run only unit tests
pytest -m unit -v

# Run only API integration tests
pytest -m api -v

# Run telemetry and monitoring tests
pytest -m monitoring -v
```

### Test Suite Execution Output
```
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\Linkific_Intern\Day 24
configfile: pytest.ini
testpaths: tests
collected 51 items

tests/api/test_health_api.py::TestHealthApi::test_root_discovery_endpoint PASSED
tests/api/test_health_api.py::TestHealthApi::test_health_check_endpoint PASSED
tests/api/test_health_api.py::TestHealthApi::test_liveness_probe_endpoint PASSED
tests/api/test_health_api.py::TestHealthApi::test_readiness_probe_endpoint PASSED
tests/api/test_health_api.py::TestHealthApi::test_request_correlation_headers PASSED
tests/api/test_metrics_api.py::TestMetricsApi::test_prometheus_metrics_scrape_endpoint PASSED
tests/api/test_metrics_api.py::TestMetricsApi::test_system_telemetry_endpoint PASSED
tests/api/test_tasks_api.py::TestTasksApi::test_create_task_success PASSED
tests/api/test_tasks_api.py::TestTasksApi::test_create_task_validation_errors PASSED
tests/api/test_tasks_api.py::TestTasksApi::test_end_to_end_lifecycle PASSED
tests/unit/test_config.py::TestConfig::test_default_settings_load PASSED
tests/unit/test_config.py::TestConfig::test_secret_key_masking PASSED
tests/unit/test_logging.py::TestLogging::test_json_formatter_produces_valid_json PASSED
tests/unit/test_monitoring.py::TestMonitoring::test_generate_prometheus_metrics PASSED
tests/unit/test_task_service.py::TestTaskService::test_execute_task_supported_types PASSED
...
============================= 51 passed in 0.27s ==============================
```

---

## 🐳 Docker & Docker Compose Guide

### 1. Build the Production Docker Image
```bash
docker build -t linkific-api:1.0.0 .
```

### 2. Run the Container Standalone
```bash
docker run -d \
  --name linkific_app \
  -p 8000:8000 \
  --env-file .env \
  linkific-api:1.0.0
```

### 3. Launch Full Stack (API + Prometheus)
```bash
docker compose up -d
```
Services exposed:
- **FastAPI Application**: [http://localhost:8000](http://localhost:8000)
- **Prometheus Dashboard**: [http://localhost:9090](http://localhost:9090)

### 4. Verify Prometheus Scraping
Open [http://localhost:9090/targets](http://localhost:9090/targets) to see the `linkific_api` target in **UP** state.

---

## 📊 Monitoring & Telemetry Reference

### Available Endpoints
| Method | Path | Description | Response Type |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Full system health check with memory & disk thresholds | JSON (`HealthCheckResponse`) |
| `GET` | `/health/live` | Container liveness probe | JSON (`LivenessResponse`) |
| `GET` | `/health/ready` | Ingress readiness probe | JSON (`ReadinessResponse`) |
| `GET` | `/metrics` | Prometheus metrics scrape endpoint | `text/plain` |
| `GET` | `/api/v1/telemetry` | Real-time CPU, RAM, Disk, and Process stats | JSON (`SystemTelemetryResponse`) |

### Instrumented Prometheus Metrics
- `http_requests_total{method, endpoint, status}`: Cumulative count of processed HTTP requests.
- `http_request_duration_seconds{method, endpoint}`: Latency histogram for request profiling.
- `http_active_requests`: Number of active concurrent requests in flight.
- `task_executions_total{task_type, status}`: Counter for business tasks completed.
- `system_cpu_usage_percent`: Current host/container CPU percentage.
- `system_memory_usage_percent`: Current host/container memory percentage.

---

## 📡 API Endpoint Reference

### Task Management API
- **Create Task**: `POST /api/v1/tasks`
  ```json
  // Request
  {
    "title": "Run Unit Test Suite",
    "task_type": "unit_test",
    "priority": "high",
    "payload": {"framework": "pytest"}
  }
  // Response (201 Created)
  {
    "task_id": "c1f7b0e5-7e04-4c40-9774-8b1b590e8c14",
    "title": "Run Unit Test Suite",
    "task_type": "unit_test",
    "priority": "high",
    "status": "pending",
    "result": null,
    "error": null,
    "created_at": "2026-09-28T18:40:00+00:00"
  }
  ```

- **Execute Task**: `POST /api/v1/tasks/{task_id}/execute`
  ```json
  // Response (200 OK)
  {
    "task_id": "c1f7b0e5-7e04-4c40-9774-8b1b590e8c14",
    "status": "completed",
    "result": {
      "test_suite": "Run Unit Test Suite",
      "assertions_passed": "24",
      "coverage_pct": "98.5%",
      "status": "PASSED"
    },
    "execution_time_ms": 1.12
  }
  ```

- **Get Task**: `GET /api/v1/tasks/{task_id}`
- **List Tasks**: `GET /api/v1/tasks?status=completed`
- **Delete Task**: `DELETE /api/v1/tasks/{task_id}`

---

## 📑 Deliverables Cross-Reference

| Deliverable | File Link | Description |
| :--- | :--- | :--- |
| **Deployment Checklist** | [`DEPLOYMENT_CHECKLIST.md`](./DEPLOYMENT_CHECKLIST.md) | Exhaustive gate checklist covering Testing, Logging, Env Vars, Docker, Docs, Security and Monitoring. |
| **Production Readiness Report** | [`PRODUCTION_READINESS_REPORT.md`](./PRODUCTION_READINESS_REPORT.md) | Comprehensive review report, test execution breakdown, architecture audit and production maturity scorecard. |
| **Updated README** | [`README.md`](./README.md) | Architectural documentation, operational guide, testing and docker execution instructions. |
