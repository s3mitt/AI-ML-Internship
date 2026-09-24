# FastAPI Async Performance Demo

A production-structured, beginner-friendly FastAPI application engineered to demonstrate and benchmark **Synchronous vs. Asynchronous API Execution**, **Middleware Diagnostics**, **BackgroundTasks**, **Dependency Injection**, and **API Versioning**.

Built from scratch as part of the backend engineering internship curriculum.

---

## 1. Project Overview

Modern web applications spend most of their execution time waiting for I/O operations (database queries, network API requests, cache lookups, or file transfers). This project demonstrates:
- How synchronous endpoints (`def` with `time.sleep`) block threads and depend on worker thread pools.
- How asynchronous endpoints (`async def` with `await asyncio.sleep`) leverage non-blocking cooperative multitasking to handle concurrent traffic with lower latency and higher throughput.
- How supporting production patterns (timing middleware, background logging, dependency injection, and versioning) integrate seamlessly in FastAPI.

---

## 2. Learning Objectives

- **Async Programming & Concurrency**: Understanding Python coroutines and cooperative event loop scheduling.
- **Async/Await Syntax**: Proper non-blocking pattern usage vs blocking anti-patterns.
- **Middleware Engineering**: Intercepting requests, timing execution, and appending custom headers (`X-Process-Time`).
- **Background Tasks**: Offloading non-critical operations (audit logging) to prevent response latency.
- **Dependency Injection**: Using FastAPI's `Depends` to decouple request context and service instantiation.
- **Pydantic Validation**: Strong request and response schemas preventing invalid states (e.g., negative prices/quantities).
- **API Versioning**: Structuring routes using versioned `APIRouter` modules (`/api/v1`).
- **Automated Testing**: Complete test coverage using `pytest` and `TestClient`.
- **Benchmarking & Analysis**: Concurrent load testing using `httpx` and `asyncio` with real empirical metrics.

---

## 3. Technologies Used

- **Language**: Python 3.12+
- **Web Framework**: FastAPI 0.115.0
- **ASGI Server**: Uvicorn 0.32.0
- **Validation**: Pydantic v2 (2.9.2)
- **HTTP & Benchmark Client**: HTTPX 0.28.1 & asyncio
- **Test Framework**: Pytest 9.1.1 & Starlette TestClient

---

## 4. Project Structure

```text
Day 21/
├── app/
│   ├── __init__.py               # Package metadata
│   ├── main.py                   # FastAPI initialization, middleware, & router mounts
│   │
│   ├── api/                      # Versioned API controllers
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routes.py         # Sync & async endpoints, OpenAPI metadata
│   │
│   ├── dependencies/             # Dependency injection providers
│   │   ├── __init__.py
│   │   └── dependencies.py       # RequestContext & ItemService providers
│   │
│   ├── middleware/               # Application-level middlewares
│   │   ├── __init__.py
│   │   └── timing.py             # TimingMiddleware (logs & X-Process-Time header)
│   │
│   ├── models/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py            # ItemCreate (validation) & ItemResponse
│   │
│   └── services/                 # Business logic layer
│       ├── __init__.py
│       └── service.py            # Sync & async processing, background audit logger
│
├── tests/
│   ├── __init__.py
│   └── test_api.py               # 11 automated pytest tests covering all requirements
│
├── scripts/
│   └── benchmark.py              # Concurrent benchmark tool (httpx + asyncio)
│
├── docs/
│   ├── API_DOCUMENTATION.md      # Detailed endpoint specifications & curl examples
│   ├── BENCHMARK_REPORT.md       # Comprehensive empirical performance report
│   └── PERFORMANCE_COMPARISON.md # Side-by-side architecture & latency comparisons
│
├── logs/
│   ├── .gitkeep
│   └── background_tasks.log      # Output destination for non-critical audit tasks
│
├── benchmark_results.json        # Machine-readable output from latest benchmark run
├── requirements.txt              # Minimal production dependencies
├── README.md                     # Project documentation & runbook
└── .gitignore                    # Git ignore file
```

---

## 5. Installation & Setup

### Step 1: Create Virtual Environment (Optional but recommended)
```bash
# In the project root (D:\Linkific_Intern\Day 21)
python -m venv venv

# Activate on Windows (PowerShell):
venv\Scripts\Activate.ps1

# Activate on Windows (Command Prompt):
venv\Scripts\activate.bat
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 6. Running the Application

Start the development server with Uvicorn:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Server output will confirm:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

---

## 7. Interactive API Documentation

FastAPI automatically generates interactive OpenAPI documentation:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Raw OpenAPI Schema**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 8. Example Requests & Responses

### 1. Synchronous Endpoint (`POST /api/v1/items/sync`)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/items/sync" \
     -H "Content-Type: application/json" \
     -d '{"name": "Mechanical Keyboard", "quantity": 2, "price": 4500.0}'
```

**Response (`200 OK`)**:
```json
{
  "id": "24bef148-b7a1-46a5-91d3-3a43979e22aa",
  "name": "Mechanical Keyboard",
  "quantity": 2,
  "price": 4500.0,
  "total_price": 9000.0,
  "status": "completed",
  "processing_type": "sync",
  "processed_at": "2026-09-24T12:25:01.336306+00:00",
  "message": "Item 'Mechanical Keyboard' processed successfully via synchronous pipeline."
}
```
**Injected Response Header**: `X-Process-Time: 0.056635`

### 2. Asynchronous Endpoint (`POST /api/v1/items/async`)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/items/async" \
     -H "Content-Type: application/json" \
     -d '{"name": "Ergonomic Mouse", "quantity": 1, "price": 2500.0}'
```

**Response (`200 OK`)**:
```json
{
  "id": "9ee12b49-8987-41d7-a676-6b8658e05cd1",
  "name": "Ergonomic Mouse",
  "quantity": 1,
  "price": 2500.0,
  "total_price": 2500.0,
  "status": "completed",
  "processing_type": "async",
  "processed_at": "2026-09-24T12:25:01.409476+00:00",
  "message": "Item 'Ergonomic Mouse' processed successfully via asynchronous pipeline."
}
```
**Injected Response Header**: `X-Process-Time: 0.052140`

### 3. Validation Rejection (`422 Unprocessable Entity`)

Sending negative quantity:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/items/async" \
     -H "Content-Type: application/json" \
     -d '{"name": "USB Cable", "quantity": -5, "price": 200.0}'
```
**Response**:
```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "quantity"],
      "msg": "Input should be greater than 0",
      "input": -5,
      "ctx": { "gt": 0 }
    }
  ]
}
```

---

## 9. Running Automated Tests

Run the full pytest suite:
```bash
pytest -v
```

### Verified Test Results (11 Passed):
```text
tests/test_api.py::test_root_endpoint PASSED                             [  9%]
tests/test_api.py::test_1_sync_endpoint_success PASSED                   [ 18%]
tests/test_api.py::test_2_async_endpoint_success PASSED                  [ 27%]
tests/test_api.py::test_3_response_structure_validation PASSED           [ 36%]
tests/test_api.py::test_4_validation_rejects_invalid_quantity PASSED     [ 45%]
tests/test_api.py::test_5_validation_rejects_invalid_price PASSED        [ 54%]
tests/test_api.py::test_6_validation_rejects_missing_fields PASSED       [ 63%]
tests/test_api.py::test_7_middleware_adds_x_process_time_header PASSED   [ 72%]
tests/test_api.py::test_8_api_versioning_works PASSED                    [ 81%]
tests/test_api.py::test_9_background_task_is_triggered PASSED            [ 90%]
tests/test_api.py::test_10_dependency_injection_works PASSED             [100%]
============================= 11 passed in 1.23s ==============================
```

---

## 10. Running the Benchmark

Make sure the server is running on port 8000, then execute:

```bash
python scripts/benchmark.py --requests 100 --concurrency 10
```

To run with custom parameters:
```bash
python scripts/benchmark.py --url http://127.0.0.1:8000 --requests 200 --concurrency 20 --output benchmark_results.json
```

---

## 11. Actual Benchmark Results

The following table contains **real measured metrics** captured by running the benchmark tool against the live server:

| Metric | Synchronous (`def`) | Asynchronous (`async def`) | Improvement |
|---|---:|---:|---:|
| **Total Requests** | 100 | 100 | — |
| **Concurrency** | 10 | 10 | — |
| **Total Wall-Clock Time** | `0.803 s` | `0.788 s` | **+1.89% faster** |
| **Throughput (req/s)** | `124.49 req/s` | `126.89 req/s` | **+1.93% higher** |
| **Average Latency** | `75.90 ms` | `73.89 ms` | **+2.65% lower** |
| **Median (P50)** | `76.50 ms` | `72.42 ms` | **+5.33% lower** |
| **P95 Latency** | `97.03 ms` | `93.10 ms` | **+4.05% lower** |
| **P99 Latency** | `101.88 ms` | `108.48 ms` | `-6.48%` |
| **Min Latency** | `56.05 ms` | `51.74 ms` | **+7.69% lower** |
| **Max Latency** | `109.29 ms` | `112.79 ms` | `-3.20%` |

*(Under higher concurrency of 50 connections across 200 requests, async demonstrated **+9.97% higher throughput** and **+12.31% lower average latency** due to avoiding threadpool saturation).*

---

## 12. Core Concepts Explained for Interview / Review

### 1. Synchronous vs. Asynchronous Execution
- **Synchronous (`def`)**: When an endpoint function is declared with standard `def`, FastAPI executes it on an external threadpool (`anyio.to_thread.run_sync`). When it hits a blocking call like `time.sleep()`, that specific OS worker thread is frozen. Thread switching has memory and scheduling overhead.
- **Asynchronous (`async def`)**: Declares a Python coroutine. When it encounters `await asyncio.sleep()`, it yields control back to the event loop. The single thread event loop is immediately free to serve other incoming network requests.

### 2. Timing Middleware
- `TimingMiddleware` subclasses Starlette's `BaseHTTPMiddleware`.
- It records start time using `time.perf_counter()`, executes downstream handlers with `await call_next(request)`, computes the elapsed duration, logs the request (`POST /api/v1/items/async - 200 - 0.0521s`), and injects `X-Process-Time` into the response headers.

### 3. Background Tasks
- Dispatched via FastAPI's `BackgroundTasks.add_task(func, *args)`.
- It executes after the HTTP response has been sent to the client. This is ideal for non-critical side effects like audit logging, metrics emission, or sending emails. Critical database writes should remain within the request-response lifecycle.

### 4. Dependency Injection
- Powered by `Depends()`.
- The endpoint declares dependencies (`service: ItemService = Depends(get_item_service)`, `context: RequestContext = Depends(get_request_context)`).
- This decouples business logic from HTTP routing and allows trivial mocking in unit tests using `app.dependency_overrides`.

### 5. API Versioning
- Uses FastAPI's `APIRouter(prefix="/items")` mounted under `app.include_router(api_v1_router, prefix="/api/v1")`.
- This creates clean namespaces (`/api/v1/...`) and ensures new versions (`/api/v2/...`) can be introduced in isolated modules without breaking existing API consumers.
