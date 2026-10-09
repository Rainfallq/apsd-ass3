"""Command line entry point: python -m streamwin.cli"""

from __future__ import annotations

import argparse
from functools import partial

from .adaptive import static_policy, threshold_policy, utilization_policy
from .loadgen import make_profile
from .plotting import plot_latency
from .simulator import CostModel, SimResult, simulate


def run(out: str | None = None) -> dict[str, SimResult]:
    model = CostModel()
    profile = make_profile()
    policies = {
        "static 100 ms": static_policy(100),
        "static 1000 ms": static_policy(1000),
        "static 5000 ms": static_policy(5000),
        "adaptive (threshold)": threshold_policy,
        "adaptive (utilization)": partial(
            utilization_policy, overhead_ms=model.overhead_ms, per_txn_ms=model.per_txn_ms
        ),
    }
    results = {name: simulate(profile, pol, model) for name, pol in policies.items()}

    print(f"{'policy':<24}{'avg ms':>12}{'max ms':>14}{'overloaded s':>15}")
    for name, res in results.items():
        print(
            f"{name:<24}{res.avg_latency_ms:>12.1f}{res.max_latency_ms:>14.1f}"
            f"{res.overloaded_seconds:>15d}"
        )

    if out:
        plot_latency(results, out)
        print(f"chart saved to {out}")
    return results


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compare static and adaptive windows.")
    parser.add_argument("--out", help="path for the PNG chart", default=None)
    args = parser.parse_args(argv)
    run(args.out)


if __name__ == "__main__":
    main()
