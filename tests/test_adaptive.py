import pytest

from streamwin.adaptive import (
    CANDIDATE_WINDOWS_MS,
    static_policy,
    threshold_policy,
    utilization_policy,
)


def test_static_policy_returns_same_window():
    policy = static_policy(500)
    assert policy(10, 0, 0) == 500
    assert policy(9000, 300, 0.9) == 500


@pytest.mark.parametrize("bad", [10, 6000])
def test_static_policy_rejects_out_of_range(bad):
    with pytest.raises(ValueError):
        static_policy(bad)


@pytest.mark.parametrize(
    "load, expected",
    [(0, 100), (999, 100), (1000, 500), (4999, 500), (5000, 2000), (20000, 2000)],
)
def test_threshold_policy_by_load(load, expected):
    assert threshold_policy(load) == expected


def test_threshold_policy_grows_when_queue_is_slow():
    assert threshold_policy(500, queue_latency_ms=150) == 150


def test_threshold_policy_grows_when_cpu_is_high():
    assert threshold_policy(500, cpu_usage=0.9) == 125


def test_threshold_policy_never_exceeds_max():
    assert threshold_policy(50000, queue_latency_ms=500, cpu_usage=1.0) <= 5000


@pytest.mark.parametrize("args", [(-1, 0, 0), (1, -5, 0), (1, 0, 1.5), (1, 0, -0.1)])
def test_threshold_policy_validates_input(args):
    with pytest.raises(ValueError):
        threshold_policy(*args)


def test_utilization_policy_low_load_uses_small_window():
    assert utilization_policy(100) == 100


def test_utilization_policy_window_does_not_shrink_when_load_grows():
    loads = [100, 1000, 3000, 8000, 20000]
    windows = [utilization_policy(load) for load in loads]
    assert windows == sorted(windows)


def test_utilization_policy_respects_target_when_possible():
    load, overhead, per_txn, target = 3000, 40.0, 0.08, 0.7
    window = utilization_policy(load, overhead_ms=overhead, per_txn_ms=per_txn, target_util=target)
    busy = overhead + load * window / 1000 * per_txn
    assert busy / window <= target


def test_utilization_policy_falls_back_to_biggest_window():
    assert utilization_policy(1_000_000) == CANDIDATE_WINDOWS_MS[-1]


def test_utilization_policy_rejects_bad_target():
    with pytest.raises(ValueError):
        utilization_policy(100, target_util=0)
