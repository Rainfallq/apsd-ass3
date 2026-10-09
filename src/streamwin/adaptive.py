"""Window size policies.

A policy is a function that takes the current state of the stream and returns
the window size in milliseconds. All policies share one signature so the
simulator can swap them freely:

    policy(load_msg_s, queue_latency_ms, cpu_usage) -> window_ms
"""

from __future__ import annotations

from collections.abc import Callable

Policy = Callable[[float, float, float], float]

MIN_WINDOW_MS = 100.0
MAX_WINDOW_MS = 5000.0
CANDIDATE_WINDOWS_MS = (100.0, 250.0, 500.0, 1000.0, 2000.0, 5000.0)


def _check_inputs(load_msg_s: float, queue_latency_ms: float, cpu_usage: float) -> None:
    if load_msg_s < 0:
        raise ValueError("load_msg_s must not be negative")
    if queue_latency_ms < 0:
        raise ValueError("queue_latency_ms must not be negative")
    if not 0.0 <= cpu_usage <= 1.0:
        raise ValueError("cpu_usage must be between 0 and 1")


def static_policy(window_ms: float) -> Policy:
    """Baseline: always the same window, whatever the load is."""
    if not MIN_WINDOW_MS <= window_ms <= MAX_WINDOW_MS:
        raise ValueError(f"window_ms must be between {MIN_WINDOW_MS} and {MAX_WINDOW_MS}")

    def policy(load_msg_s: float, queue_latency_ms: float = 0.0, cpu_usage: float = 0.0) -> float:
        _check_inputs(load_msg_s, queue_latency_ms, cpu_usage)
        return window_ms

    return policy


def threshold_policy(
    load_msg_s: float, queue_latency_ms: float = 0.0, cpu_usage: float = 0.0
) -> float:
    """Simple rule based policy.

    Low load gets a small window, high load gets a big one. If the queue is
    already backing up or the CPU is almost full, the window grows a bit more.
    """
    _check_inputs(load_msg_s, queue_latency_ms, cpu_usage)

    if load_msg_s < 1000:
        window = 100.0
    elif load_msg_s < 5000:
        window = 500.0
    else:
        window = 2000.0

    if queue_latency_ms > 100:
        window *= 1.5
    if cpu_usage > 0.85:
        window *= 1.25

    return min(max(window, MIN_WINDOW_MS), MAX_WINDOW_MS)


def utilization_policy(
    load_msg_s: float,
    queue_latency_ms: float = 0.0,
    cpu_usage: float = 0.0,
    *,
    overhead_ms: float = 40.0,
    per_txn_ms: float = 0.08,
    target_util: float = 0.7,
) -> float:
    """Pick the smallest candidate window that keeps the worker under target_util.

    It needs an estimate of the fixed cost per window and the cost per
    transaction. In a real system these would come from measurements.
    """
    _check_inputs(load_msg_s, queue_latency_ms, cpu_usage)
    if not 0.0 < target_util <= 1.0:
        raise ValueError("target_util must be in (0, 1]")

    for window in CANDIDATE_WINDOWS_MS:
        txns_per_window = load_msg_s * window / 1000.0
        busy_ms = overhead_ms + txns_per_window * per_txn_ms
        if busy_ms / window <= target_util:
            return window
    return CANDIDATE_WINDOWS_MS[-1]
