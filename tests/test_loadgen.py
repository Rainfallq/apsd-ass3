import pytest

from streamwin.loadgen import make_profile, synthetic_transactions


def test_default_profile_length():
    assert len(make_profile()) == 420


def test_custom_profile_values():
    assert make_profile([(2, 100), (1, 5)]) == [100.0, 100.0, 5.0]


@pytest.mark.parametrize("phases", [[], [(0, 10)], [(5, -1)]])
def test_profile_rejects_bad_phases(phases):
    with pytest.raises(ValueError):
        make_profile(phases)


def test_synthetic_transactions_are_reproducible():
    assert synthetic_transactions(20, seed=1) == synthetic_transactions(20, seed=1)


def test_synthetic_transactions_have_expected_fields():
    txn = synthetic_transactions(1)[0]
    assert set(txn) == {"txn_id", "amount", "merchant_id", "is_fraud"}
    assert 1 <= txn["amount"] <= 10000


def test_fraud_rate_extremes():
    assert all(t["is_fraud"] == 0 for t in synthetic_transactions(50, fraud_rate=0.0))
    assert all(t["is_fraud"] == 1 for t in synthetic_transactions(50, fraud_rate=1.0))


def test_synthetic_transactions_validation():
    with pytest.raises(ValueError):
        synthetic_transactions(-1)
    with pytest.raises(ValueError):
        synthetic_transactions(5, fraud_rate=2)
