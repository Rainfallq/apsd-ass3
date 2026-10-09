import pytest

from streamwin.cli import main, run
from streamwin.plotting import plot_latency


def test_run_returns_all_policies():
    results = run()
    assert len(results) == 5


def test_main_creates_chart(tmp_path, capsys):
    out = tmp_path / "chart.png"
    main(["--out", str(out)])
    assert out.exists() and out.stat().st_size > 0
    assert "avg ms" in capsys.readouterr().out


def test_plot_rejects_empty_results(tmp_path):
    with pytest.raises(ValueError):
        plot_latency({}, tmp_path / "x.png")
