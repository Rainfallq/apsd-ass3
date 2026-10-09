"""Load profiles and synthetic transactions."""

from __future__ import annotations

import random
import uuid
from typing import Any

# (seconds, messages per second)
DEFAULT_PHASES = [(60, 500), (120, 3000), (60, 8000), (120, 3000), (60, 500)]


def make_profile(phases: list[tuple[int, float]] | None = None) -> list[float]:
    """Turn a list of (seconds, load) phases into one load value per second."""
    phases = DEFAULT_PHASES if phases is None else phases
    if not phases:
        raise ValueError("phases must not be empty")

    profile: list[float] = []
    for seconds, load in phases:
        if seconds <= 0:
            raise ValueError("phase length must be positive")
        if load < 0:
            raise ValueError("load must not be negative")
        profile.extend([float(load)] * seconds)
    return profile


def synthetic_transactions(
    n: int, seed: int = 42, fraud_rate: float = 0.01
) -> list[dict[str, Any]]:
    """Generate n fake transactions. Same seed gives the same data."""
    if n < 0:
        raise ValueError("n must not be negative")
    if not 0.0 <= fraud_rate <= 1.0:
        raise ValueError("fraud_rate must be between 0 and 1")

    rng = random.Random(seed)
    result = []
    for _ in range(n):
        result.append(
            {
                "txn_id": str(uuid.UUID(int=rng.getrandbits(128), version=4)),
                "amount": round(rng.uniform(1, 10000), 2),
                "merchant_id": rng.randint(1, 10000),
                "is_fraud": int(rng.random() < fraud_rate),
            }
        )
    return result
