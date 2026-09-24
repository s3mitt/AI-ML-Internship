# Performance Comparison: Synchronous vs. Asynchronous FastAPI

This document provides a feature-by-feature and metric-by-metric comparison between the **Synchronous** (`/api/v1/items/sync`) and **Asynchronous** (`/api/v1/items/async`) endpoints implemented in this project.

All numerical figures represent **actual measurements** obtained from running `scripts/benchmark.py` against the live Uvicorn ASGI server.

---

## 1. Feature & Architecture Comparison

| Architectural Feature | Synchronous API (`/api/v1/items/sync`) | Asynchronous API (`/api/v1/items/async`) | Key Takeaway for Review/Interview |
|---|---|---|---|
| **Python Definition** | Standard function: `def process_item_sync(...)` | Coroutine function: `async def process_item_async(...)` | `async def` flags the function as a coroutine that produces an awaitable object. |
| **Simulated I/O Primitive** | Blocking call: `time.sleep(0.05)` | Non-blocking coroutine: `await asyncio.sleep(0.05)` | `time.sleep()` freezes the active OS thread; `await asyncio.sleep()` hands control back to the event loop. |
| **Event Loop Blocking** | **Yes** (if executed directly on the loop; mitigated by FastAPI threadpool) | **No** (cooperative non-blocking multitasking) | FastAPI offloads sync `def` to an external threadpool so it doesn't block the ASGI loop. |
| **Execution Context** | Dispatched to external threadpool worker (`anyio.to_thread.run_sync`) | Runs directly on the main event loop thread | Threadpools consume stack memory (~8MB per thread) and require OS context switching. |
| **Concurrency Scaling Limit** | Constrained by worker threadpool size (default ~40 threads) | Capable of handling thousands of open connections on a single thread | High concurrency leads to thread queueing in sync mode; async multiplexes via I/O events. |
| **Best Suited Use Case** | CPU-bound calculations, legacy synchronous libraries (e.g., standard `sqlite3`, `requests`) | I/O-bound web operations (external REST APIs, database queries with `asyncpg`, streaming) | Choose async for I/O scalability; choose sync/process pools for heavy computation. |

---

## 2. Actual Benchmark Measurements

Benchmark configuration: **100 requests**, **Concurrency = 10**, Payload: `{"name": "Benchmark Laptop", "quantity": 2, "price": 75000.0}`.

| Performance Metric | Sync API (`/api/v1/items/sync`) | Async API (`/api/v1/items/async`) | Relative Difference / Improvement |
|---|---:|---:|---:|
| **Total Wall Time** | `0.8033 s` | `0.7881 s` | **+1.89% faster** |
| **Throughput (Requests/sec)** | `124.49 req/s` | `126.89 req/s` | **+1.93% higher throughput** |
| **Average Latency** | `75.90 ms` | `73.89 ms` | **+2.65% lower latency** |
| **Median Latency (P50)** | `76.50 ms` | `72.42 ms` | **+5.33% lower latency** |
| **P95 Latency** | `97.03 ms` | `93.10 ms` | **+4.05% lower latency** |
| **P99 Latency** | `101.88 ms` | `108.48 ms` | `-6.48%` (tail variance on Windows loopback) |
| **Min Latency** | `56.05 ms` | `51.74 ms` | **+7.69% lower minimum latency** |
| **Max Latency** | `109.29 ms` | `112.79 ms` | `-3.20%` |
| **Success Rate** | `100/100 (100%)` | `100/100 (100%)` | Identical reliability |

---

## 3. High Concurrency Stress Comparison (Concurrency = 50, 200 Requests)

When client concurrency is elevated beyond the standard threadpool limit (40 threads):

| Metric | Sync API (50 Concurrency) | Async API (50 Concurrency) | Advantage |
|---|---:|---:|---:|
| **Total Wall Time** | `2.071 s` | `1.883 s` | **+9.07% faster** |
| **Throughput (req/s)** | `96.56 req/s` | `106.19 req/s` | **+9.97% higher** |
| **Average Latency** | `463.16 ms` | `406.15 ms` | **+12.31% lower** |
| **P99 Tail Latency** | `1590.02 ms` | `1297.28 ms` | **18.4% faster tail latency** |

---

## 4. Key Takeaways for Internship Presentation

1. **Why Async Wins on I/O**:
   Instead of keeping an OS thread waiting idle during database/network latency, `async`/`await` frees the event loop to start processing the next incoming HTTP request immediately.
2. **FastAPI's Internal Mechanism**:
   FastAPI does not break when you use normal `def` functions because it automatically executes them inside a threadpool. However, threads are expensive, memory-heavy, and limited in scale.
3. **Never Block the Event Loop**:
   If you declare `async def` but use blocking code like `time.sleep()` or synchronous `requests.get()`, you freeze the entire event loop, causing all concurrent requests to stall.
