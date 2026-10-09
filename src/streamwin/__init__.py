"""streamwin: a tiny toy model for comparing static and adaptive window sizes."""

from .adaptive import (
    CANDIDATE_WINDOWS_MS,
    static_policy,
    threshold_policy,
    utilization_policy,
)
from .loadgen import make_profile, synthetic_transactions
from .simulator import CostModel, SimResult, simulate

__all__ = [
    "CANDIDATE_WINDOWS_MS",
    "CostModel",
    "SimResult",
    "make_profile",
    "simulate",
    "static_policy",
    "synthetic_transactions",
    "threshold_policy",
    "utilization_policy",
]
__version__ = "0.1.0"
