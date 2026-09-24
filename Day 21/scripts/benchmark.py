"""Automated Performance Benchmark Script.

Compares Synchronous (/api/v1/items/sync) and Asynchronous (/api/v1/items/async)
FastAPI endpoints under concurrent load using httpx and asyncio.

Calculates:
- Total requests, successes, failures
- Average, minimum, maximum latencies
- Median (P50), P95, and P99 latencies
- Total wall-clock execution time
- Requests Per Second (RPS / Throughput)
- Latency and Throughput improvement percentages

Outputs:
- Terminal formatted comparison table
- benchmark_results.json with machine-readable telemetry
"""

import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
import httpx

# Default configuration
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_TOTAL_REQUESTS = 100
DEFAULT_CONCURRENCY = 10
DEFAULT_PAYLOAD = {
    "name": "Benchmark Laptop",
    "quantity": 2,
    "price": 75000.0,
}


def calculate_percentile(data: list[float], p: float) -> float:
    """Calculate the p-th percentile of a list using linear interpolation.

    :param data: list of numeric values
    :param p: percentile (0.0 to 100.0)
    :return: interpolated percentile value
    """
    if not data:
        return 0.0
    sorted_data = sorted(data)
    if len(sorted_data) == 1:
        return sorted_data[0]
    rank = (len(sorted_data) - 1) * (p / 100.0)
    floor_idx = int(rank)
    ceil_idx = min(floor_idx + 1, len(sorted_data) - 1)
    weight = rank - floor_idx
    return sorted_data[floor_idx] * (1.0 - weight) + sorted_data[ceil_idx] * weight


async def send_single_request(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
    payload: dict,
) -> dict:
    """Sends a single POST request constrained by concurrency semaphore."""
    async with semaphore:
        start_time = time.perf_counter()
        try:
            response = await client.post(url, json=payload)
            elapsed = time.perf_counter() - start_time
            is_success = response.status_code == 200
            status_code = response.status_code
        except Exception as exc:
            elapsed = time.perf_counter() - start_time
            is_success = False
            status_code = 0

        return {
            "elapsed": elapsed,
            "status_code": status_code,
            "success": is_success,
        }


async def benchmark_endpoint(
    client: httpx.AsyncClient,
    url: str,
    payload: dict,
    total_requests: int,
    concurrency: int,
    label: str,
) -> dict:
    """Executes concurrent requests against a specific endpoint and computes metrics."""
    print(f"\n---> Starting benchmark for [{label}] at {url}")
    print(f"     Requests: {total_requests} | Concurrency: {concurrency}")

    semaphore = asyncio.Semaphore(concurrency)
    wall_start = time.perf_counter()

    tasks = [
        send_single_request(client, semaphore, url, payload)
        for _ in range(total_requests)
    ]
    results = await asyncio.gather(*tasks)

    wall_total = time.perf_counter() - wall_start

    successful = sum(1 for r in results if r["success"])
    failed = total_requests - successful
    latencies = [r["elapsed"] for r in results if r["success"]]

    if not latencies:
        print(f"ERROR: All {total_requests} requests failed for {label}!")
        return {
            "label": label,
            "url": url,
            "total_requests": total_requests,
            "successful_requests": 0,
            "failed_requests": failed,
            "total_time_seconds": wall_total,
            "requests_per_second": 0.0,
            "avg_latency_ms": 0.0,
            "min_latency_ms": 0.0,
            "max_latency_ms": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "p99_latency_ms": 0.0,
        }

    # Convert to milliseconds for standard reporting
    latencies_ms = [l * 1000.0 for l in latencies]
    avg_latency = sum(latencies_ms) / len(latencies_ms)
    min_latency = min(latencies_ms)
    max_latency = max(latencies_ms)
    p50_latency = calculate_percentile(latencies_ms, 50.0)
    p95_latency = calculate_percentile(latencies_ms, 95.0)
    p99_latency = calculate_percentile(latencies_ms, 99.0)
    rps = total_requests / wall_total if wall_total > 0 else 0.0

    print(f"     Completed in {wall_total:.3f}s | Success: {successful}/{total_requests}")
    print(f"     Avg Latency: {avg_latency:.2f}ms | RPS: {rps:.2f} req/s")

    return {
        "label": label,
        "url": url,
        "total_requests": total_requests,
        "successful_requests": successful,
        "failed_requests": failed,
        "total_time_seconds": round(wall_total, 4),
        "requests_per_second": round(rps, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "min_latency_ms": round(min_latency, 2),
        "max_latency_ms": round(max_latency, 2),
        "p50_latency_ms": round(p50_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
        "p99_latency_ms": round(p99_latency, 2),
    }


async def run_benchmark(
    base_url: str,
    total_requests: int,
    concurrency: int,
    output_file: str,
):
    """Orchestrates benchmark runs across both sync and async endpoints."""
    # Check server availability
    async with httpx.AsyncClient(timeout=10.0) as check_client:
        try:
            resp = await check_client.get(f"{base_url}/")
            if resp.status_code != 200:
                print(f"Warning: Root endpoint returned status {resp.status_code}")
        except Exception as e:
            print(f"\n[CRITICAL ERROR] Unable to connect to server at {base_url}.")
            print("Please ensure the FastAPI server is running before executing the benchmark:")
            print("  uvicorn app.main:app --host 127.0.0.1 --port 8000")
            print(f"Details: {e}")
            sys.exit(1)

    sync_url = f"{base_url}/api/v1/items/sync"
    async_url = f"{base_url}/api/v1/items/async"

    # Configure HTTP client with large connection pool to prevent socket contention
    limits = httpx.Limits(
        max_connections=concurrency * 2, max_keepalive_connections=concurrency
    )

    async with httpx.AsyncClient(limits=limits, timeout=60.0) as client:
        # Run Synchronous Benchmark
        sync_metrics = await benchmark_endpoint(
            client=client,
            url=sync_url,
            payload=DEFAULT_PAYLOAD,
            total_requests=total_requests,
            concurrency=concurrency,
            label="Synchronous (def)",
        )

        # Allow system sockets and event loop to settle
        print("\nCooling down for 2 seconds...")
        await asyncio.sleep(2.0)

        # Run Asynchronous Benchmark
        async_metrics = await benchmark_endpoint(
            client=client,
            url=async_url,
            payload=DEFAULT_PAYLOAD,
            total_requests=total_requests,
            concurrency=concurrency,
            label="Asynchronous (async def)",
        )

    # Compute comparative improvements
    sync_time = sync_metrics["total_time_seconds"]
    async_time = async_metrics["total_time_seconds"]
    sync_avg = sync_metrics["avg_latency_ms"]
    async_avg = async_metrics["avg_latency_ms"]
    sync_rps = sync_metrics["requests_per_second"]
    async_rps = async_metrics["requests_per_second"]

    # Total time reduction: ((Sync - Async) / Sync) * 100
    time_improvement = (
        ((sync_time - async_time) / sync_time) * 100.0 if sync_time > 0 else 0.0
    )
    # Average latency improvement: ((Sync - Async) / Sync) * 100
    latency_improvement = (
        ((sync_avg - async_avg) / sync_avg) * 100.0 if sync_avg > 0 else 0.0
    )
    # Throughput improvement: ((Async - Sync) / Sync) * 100
    throughput_improvement = (
        ((async_rps - sync_rps) / sync_rps) * 100.0 if sync_rps > 0 else 0.0
    )

    comparison = {
        "total_time_improvement_pct": round(time_improvement, 2),
        "avg_latency_improvement_pct": round(latency_improvement, 2),
        "throughput_improvement_pct": round(throughput_improvement, 2),
    }

    final_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "base_url": base_url,
            "total_requests": total_requests,
            "concurrency": concurrency,
            "payload": DEFAULT_PAYLOAD,
        },
        "sync_endpoint": sync_metrics,
        "async_endpoint": async_metrics,
        "improvements": comparison,
    }

    # Save to disk
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)

    # Print summary table
    print("\n" + "=" * 78)
    print("                 BENCHMARK PERFORMANCE SUMMARY TABLE                  ")
    print("=" * 78)
    print(
        f"{'Metric':<25} | {'Synchronous':<16} | {'Asynchronous':<16} | {'Improvement':<12}"
    )
    print("-" * 78)
    print(
        f"{'Total Requests':<25} | {sync_metrics['total_requests']:<16} | {async_metrics['total_requests']:<16} | {'-':<12}"
    )
    print(
        f"{'Concurrency':<25} | {concurrency:<16} | {concurrency:<16} | {'-':<12}"
    )
    print(
        f"{'Total Wall Time (s)':<25} | {sync_metrics['total_time_seconds']:<16.3f} | {async_metrics['total_time_seconds']:<16.3f} | {time_improvement:>+8.2f}%"
    )
    print(
        f"{'Throughput (req/s)':<25} | {sync_metrics['requests_per_second']:<16.2f} | {async_metrics['requests_per_second']:<16.2f} | {throughput_improvement:>+8.2f}%"
    )
    print(
        f"{'Avg Latency (ms)':<25} | {sync_metrics['avg_latency_ms']:<16.2f} | {async_metrics['avg_latency_ms']:<16.2f} | {latency_improvement:>+8.2f}%"
    )
    print(
        f"{'Median Latency / P50 (ms)':<25} | {sync_metrics['p50_latency_ms']:<16.2f} | {async_metrics['p50_latency_ms']:<16.2f} | {'-':<12}"
    )
    print(
        f"{'P95 Latency (ms)':<25} | {sync_metrics['p95_latency_ms']:<16.2f} | {async_metrics['p95_latency_ms']:<16.2f} | {'-':<12}"
    )
    print(
        f"{'P99 Latency (ms)':<25} | {sync_metrics['p99_latency_ms']:<16.2f} | {async_metrics['p99_latency_ms']:<16.2f} | {'-':<12}"
    )
    print(
        f"{'Min Latency (ms)':<25} | {sync_metrics['min_latency_ms']:<16.2f} | {async_metrics['min_latency_ms']:<16.2f} | {'-':<12}"
    )
    print(
        f"{'Max Latency (ms)':<25} | {sync_metrics['max_latency_ms']:<16.2f} | {async_metrics['max_latency_ms']:<16.2f} | {'-':<12}"
    )
    print("=" * 78)
    print(f"Results successfully saved to: {output_path.resolve()}\n")


def main():
    parser = argparse.ArgumentParser(
        description="FastAPI Sync vs Async Performance Benchmarker"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_BASE_URL,
        help=f"Base URL of running FastAPI server (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=DEFAULT_TOTAL_REQUESTS,
        help=f"Total requests per endpoint (default: {DEFAULT_TOTAL_REQUESTS})",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Number of concurrent requests (default: {DEFAULT_CONCURRENCY})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmark_results.json",
        help="Path to output JSON file (default: benchmark_results.json)",
    )

    args = parser.parse_args()
    asyncio.run(
        run_benchmark(
            base_url=args.url,
            total_requests=args.requests,
            concurrency=args.concurrency,
            output_file=args.output,
        )
    )


if __name__ == "__main__":
    main()
