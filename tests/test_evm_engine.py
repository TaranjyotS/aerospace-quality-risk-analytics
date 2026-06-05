import pandas as pd
import pytest

from app.evm_engine import calculate_evm_metrics, evm_summary


def test_calculate_evm_metrics():
    frame = pd.DataFrame(
        {
            "Time Period": ["M1"],
            "Cost": [100],
            "PV": [1000],
            "AC": [800],
            "EV": [900],
        }
    )
    result = calculate_evm_metrics(frame)
    assert result.loc[0, "cost_variance"] == 100
    assert result.loc[0, "schedule_variance"] == -100
    assert result.loc[0, "cost_performance_index"] == 1.125
    assert result.loc[0, "schedule_performance_index"] == 0.9
    assert result.loc[0, "status"] == "Schedule risk"


def test_calculate_evm_metrics_requires_columns():
    with pytest.raises(ValueError):
        calculate_evm_metrics(pd.DataFrame({"PV": [1]}))


def test_evm_summary_uses_latest_period():
    frame = pd.DataFrame(
        {
            "Time Period": ["M1", "M2"],
            "Cost": [100, 200],
            "PV": [1000, 1000],
            "AC": [1000, 1100],
            "EV": [1000, 1000],
        }
    )
    metrics = calculate_evm_metrics(frame)
    summary = evm_summary(metrics)
    assert summary["periods"] == 2
    assert summary["latest_period"] == "M2"
    assert summary["latest_cpi"] == 0.9091
