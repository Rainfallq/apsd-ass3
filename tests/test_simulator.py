import pytest

from streamwin.adaptive import static_policy, threshold_policy
from streamwin.simulator import CostModel, simulate


def test_light_load_has_no_overload():
    res = simulate([100.0] * 30, static_policy(500))
    assert res.overloaded_seconds == 0
    assert res.max_latency_ms < 1000


def test_heavy_load_with_small_window_overloads():
    res = simulate([8000.0] * 10, static_policy(100))
    assert res.overloaded_seconds == 10
    assert res.latency_series[-1] > res.latency_series[0]


def test_backlog_drains_after_peak():
    profile = [8000.0] * 5 + [100.0] * 60
    res = simulate(profile, static_policy(100))
    assert res.latency_series[-1] < res.latency_series[4]


def test_total_txns_is_sum_of_profile():
    profile = [10.0, 20.0, 30.0]
    assert simulate(profile, static_policy(100)).total_txns == 60.0


def test_latency_series_length_matches_profile():
    profile = [500.0] * 12
    assert len(simulate(profile, threshold_policy).latency_series) == 12


def test_empty_profile_is_rejected():
    with pytest.raises(ValueError):
        simulate([], static_policy(100))


def test_zero_load_does_not_crash():
    res = simulate([0.0] * 5, static_policy(100))
    assert res.avg_latency_ms > 0


def test_cost_model_rejects_negative_costs():
    with pytest.raises(ValueError):
        CostModel(overhead_ms=-1)


def test_bigger_overhead_means_bigger_latency():
    cheap = simulate([500.0] * 10, static_policy(500), CostModel(overhead_ms=1))
    costly = simulate([500.0] * 10, static_policy(500), CostModel(overhead_ms=100))
    assert costly.avg_latency_ms > cheap.avg_latency_ms
