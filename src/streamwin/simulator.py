"""A very small fluid model of a windowed stream processor.

Every second the load is known. The policy picks a window size. Each window
costs a fixed overhead plus a cost per transaction. If the worker cannot keep
up, a backlog grows and every transaction waits longer. When there is spare
capacity the backlog shrinks again.

This is a toy model made for learning and for tests. It does not prove
anything about a real Kafka cluster.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .adaptive import Policy


@dataclass(frozen=True)
class CostModel:
    overhead_ms: float = 40.0  # fixed cost of closing one window
    per_txn_ms: float = 0.08  # cost of one transaction

    def __post_init__(self) -> None:
        if self.overhead_ms < 0 or self.per_txn_ms < 0:
            raise ValueError("costs must not be negative")


@dataclass
class SimResult:
    avg_latency_ms: float
    max_latency_ms: float
    overloaded_seconds: int
    total_txns: float
    latency_series: list[float] = field(default_factory=list)


def simulate(profile: list[float], policy: Policy, model: CostModel | None = None) -> SimResult:
    """Run the policy over a load profile (one load value per second)."""
    if not profile:
        raise ValueError("profile must not be empty")
    model = model or CostModel()

    backlog_ms = 0.0
    prev_util = 0.0
    weighted_sum = 0.0
    total_txns = 0.0
    max_latency = 0.0
    overloaded = 0
    series: list[float] = []

    for load in profile:
        window = policy(load, backlog_ms, min(prev_util, 1.0))
        txns_per_window = load * window / 1000.0
        proc_ms = model.overhead_ms + txns_per_window * model.per_txn_ms
        util = proc_ms / window  # busy share of each window

        if util > 1.0:
            backlog_ms += (util - 1.0) * 1000.0
            overloaded += 1
        else:
            backlog_ms = max(0.0, backlog_ms - (1.0 - util) * 1000.0)

        latency = window / 2.0 + proc_ms + backlog_ms
        series.append(latency)
        weighted_sum += latency * load
        total_txns += load
        max_latency = max(max_latency, latency)
        prev_util = util

    avg = weighted_sum / total_txns if total_txns > 0 else sum(series) / len(series)
    return SimResult(avg, max_latency, overloaded, total_txns, series)
