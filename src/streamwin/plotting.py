"""Plot helpers (matplotlib)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .simulator import SimResult  # noqa: E402


def plot_latency(results: dict[str, SimResult], out_path: str | Path) -> Path:
    """Save a line chart with latency over time for every policy."""
    if not results:
        raise ValueError("results must not be empty")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for name, res in results.items():
        ax.plot(res.latency_series, label=name)
    ax.set_xlabel("time, seconds")
    ax.set_ylabel("estimated latency, ms")
    ax.set_yscale("log")
    ax.set_title("Latency of different window policies (toy model)")
    ax.legend()
    fig.tight_layout()

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out
