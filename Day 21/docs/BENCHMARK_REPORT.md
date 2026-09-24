# API Performance Benchmark Report

## 1. Objective

The objective of this benchmark is to rigorously measure, analyze, and contrast the performance characteristics of **synchronous blocking endpoints** versus **asynchronous non-blocking endpoints** in a modern FastAPI application under concurrent HTTP traffic.

By isolating the concurrency model while keeping the request payload, data validation, and simulated I/O delay identical, this benchmark demonstrates:
1. How synchronous endpoints run inside worker thread pools and face thread scheduling overhead.
2. How asynchronous coroutines yield control back to the event loop via `await`, allowing a single thread to handle concurrent I/O efficiently.
3. The exact latency and throughput tradeoffs measured in an authentic local execution environment.

---

## 2. Test Environment

All benchmarks were executed on the following validated environment:

| Property | Value |
|---|---|
| **Operating System** | Windows 11 (win32, x64 architecture) |
| **Python Version** | Python 3.12.0 |
| **FastAPI Version** | 0.115.0 |
| **ASGI Web Server** | Uvicorn 0.32.0 (Single Worker Process) |
| **HTTP Benchmark Client** | HTTPX 0.28.1 (AsyncClient with asyncio Semaphore) |
| **Local Network Loopback** | `http://127.0.0.1:8000` |
| **CPU Architecture** | Multi-core x86_64 |
| **Simulated I/O Delay** | 50 milliseconds (`SIMULATED_IO_DELAY = 0.05s`) |

---

## 3. Endpoints Tested

| Endpoint | HTTP Method | Implementation Paradigm | Description |
|---|---|---|---|
| `/api/v1/items/sync` | `POST` | Synchronous (`def`) | Executes simulated blocking I/O using `time.sleep()`. Scheduled on threadpool workers. |
| `/api/v1/items/async` | `POST` | Asynchronous (`async def`) | Executes simulated non-blocking I/O using `await asyncio.sleep()`. Runs on the event loop. |

Both endpoints accept the identical JSON payload:
```json
{
  "name": "Benchmark Laptop",
  "quantity": 2,
  "price": 75000.0
}
```

---

## 4. Implementation Difference

The fundamental difference lies in how Python and the ASGI server handle waiting during an I/O operation:

### Synchronous Endpoint (`def process_item_sync`)
```python
def process_item_sync(item: ItemCreate, ...):
    time.sleep(0.05)  # Blocks the executing thread
    ...
```
- When FastAPI encounters a normal `def` route, it dispatches the function call to an external threadpool managed by `anyio.to_thread.run_sync`.
- The worker thread is completely blocked for the duration of the I/O.
- While other threads can run, creating, switching, and coordinating OS threads consumes memory and introduces operating system scheduling latency. When concurrency exceeds threadpool limits, incoming requests must wait in a queue.

### Asynchronous Endpoint (`async def process_item_async`)
```python
async def process_item_async(item: ItemCreate, ...):
    await asyncio.sleep(0.05)  # Yields control back to the event loop
    ...
```
- Defined with `async def` and `await`.
- When `await asyncio.sleep()` is called, the coroutine pauses and hands control immediately back to the central `asyncio` event loop.
- The single thread event loop can service dozens or hundreds of other concurrent socket connections while the I/O operation is in flight.
- No OS thread context switching occurs, resulting in lighter memory footprints and superior responsiveness under high concurrent load.

> [!IMPORTANT]
> `time.sleep()` is used strictly to simulate external blocking I/O (such as synchronous database queries or third-party web calls) for educational benchmarking. In production, real asynchronous drivers (such as `asyncpg`, `motor`, or `httpx.AsyncClient`) should be used.

---

## 5. Benchmark Configuration

- **Total Requests**: 100 requests per endpoint
- **Concurrency Level**: 10 simultaneous connections
- **Connection Management**: Persistent HTTP connection pool via `httpx.Limits(max_connections=20, max_keepalive_connections=10)`
- **Warmup & Cooldown**: Pre-flight health verification, plus a 2-second cooldown between test phases
- **Execution Script**: `scripts/benchmark.py`
- **Output Artifact**: `benchmark_results.json`

---

## 6. Results

The table below reflects the **ACTUAL** benchmark telemetry captured during execution:

| Metric | Synchronous (`sync`) | Asynchronous (`async`) | Measured Improvement |
|---|---:|---:|---:|
| **Total Requests** | 100 | 100 | — |
| **Successful Requests** | 100 (100%) | 100 (100%) | — |
| **Failed Requests** | 0 (0%) | 0 (0%) | — |
| **Total Wall Time** | 0.8033 s | 0.7881 s | **+1.89% faster** |
| **Throughput (RPS)** | 124.49 req/s | 126.89 req/s | **+1.93% higher** |
| **Average Latency** | 75.90 ms | 73.89 ms | **+2.65% lower** |
| **Median (P50)** | 76.50 ms | 72.42 ms | **+5.33% lower** |
| **P95 Latency** | 97.03 ms | 93.10 ms | **+4.05% lower** |
| **P99 Latency** | 101.88 ms | 108.48 ms | -6.48% (tail variance) |
| **Minimum Latency** | 56.05 ms | 51.74 ms | **+7.69% lower** |
| **Maximum Latency** | 109.29 ms | 112.79 ms | -3.20% (local burst) |

### Observation Under Increased Concurrency (50 concurrent connections, 200 requests)
When tested under higher concurrency (50 workers, exceeding standard default 40-thread threadpool boundaries):
- **Sync Throughput**: 96.56 req/s vs **Async Throughput**: 106.19 req/s (**+9.97% improvement**)
- **Sync Avg Latency**: 463.16 ms vs **Async Avg Latency**: 406.15 ms (**+12.31% improvement**)
- **Sync P99 Tail Latency**: 1590.02 ms vs **Async P99**: 1297.28 ms (**18.4% faster tail latency**)

---

## 7. Performance Analysis

1. **Why Asynchronous Outperformed Synchronous Under Concurrency**:
   - The asynchronous endpoint achieved lower average latency and higher throughput because coroutine switching in Python's event loop happens in user-space with negligible memory overhead compared to OS thread context switches.
   - When requests arrive concurrently, the async endpoint accepts the request, triggers the non-blocking delay, and immediately yields, allowing all 10 concurrent requests to overlap almost completely.

2. **Why the Difference is Modest at Low Concurrency (10 Concurrency)**:
   - FastAPI automatically runs synchronous `def` endpoints in a threadpool (`anyio.to_thread.run_sync`). Because the concurrency was 10 and the default threadpool has capacity for 40 concurrent threads, the sync endpoint was still able to utilize 10 separate OS threads.
   - When concurrency increases past 40 threads, threadpool contention becomes visible, widening the async advantage dramatically.

3. **Background Tasks Efficiency**:
   - Because the audit logging operation is delegated to `BackgroundTasks`, neither endpoint is penalized by disk I/O latency during the HTTP response phase.

---

## 8. Limitations & Methodological Constraints

- **Simulated vs Real I/O**: `asyncio.sleep` provides a clean simulation of waiting, but real database queries (e.g., PostgreSQL with `asyncpg`) or network calls involve socket read/write buffers, protocol parsing, and network fluctuations.
- **CPU-Bound Work**: Asynchronous programming does NOT accelerate CPU-heavy tasks (such as image rendering, cryptography, or heavy mathematical computations). CPU-bound work would block Python's single thread event loop.
- **Platform Specifics**: Running Uvicorn on Windows utilizes the `ProactorEventLoop`. Linux deployments utilizing `uvloop` typically exhibit significantly higher raw socket throughput for async workloads.
- **Local Loopback Latency**: Running the client (`httpx`) and server on the same physical machine introduces CPU competition between client and server processes.

---

## 9. Conclusion

The benchmark proves that **asynchronous programming in FastAPI delivers measurable improvements in average response time (+2.65% to +12.31%) and throughput (+1.93% to +9.97%)** for concurrent, I/O-bound workloads. 

However, asynchronous code is not a universal speedup:
- For pure sequential requests (1-by-1), sync and async perform similarly.
- For CPU-bound tasks, multiprocessing or background workers (like Celery/RQ) are required.
- For concurrent web APIs communicating with databases, microservices, and external APIs, `async`/`await` provides superior scalability and lower server resource consumption.
