"""Earned Value Management calculations.

The original project workbook contains PV, AC, and EV values. This module turns
that static spreadsheet into reusable analytics for schedule and cost control.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"Time Period", "Cost", "PV", "AC", "EV"}


def calculate_evm_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate EVM metrics from a dataframe containing PV, AC, and EV columns."""

    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required EVM columns: {sorted(missing)}")

    data = frame.copy()
    data = data.rename(
        columns={
            "Time Period": "time_period",
            "Cost": "cost",
            "PV": "planned_value",
            "AC": "actual_cost",
            "EV": "earned_value",
        }
    )
    data["cost_variance"] = data["earned_value"] - data["actual_cost"]
    data["schedule_variance"] = data["earned_value"] - data["planned_value"]
    data["cost_performance_index"] = data["earned_value"] / data["actual_cost"]
    data["schedule_performance_index"] = data["earned_value"] / data["planned_value"]
    data["status"] = data.apply(_status_from_row, axis=1)
    return data


def _status_from_row(row: pd.Series) -> str:
    """Classify EVM health using CPI and SPI."""

    cpi = float(row["cost_performance_index"])
    spi = float(row["schedule_performance_index"])
    if cpi >= 1 and spi >= 1:
        return "On track"
    if cpi < 0.98 and spi < 0.98:
        return "Cost and schedule risk"
    if cpi < 0.98:
        return "Cost risk"
    if spi < 0.98:
        return "Schedule risk"
    return "Watch"


def load_evm_workbook(path: str | Path, sheet_name: str = "Sheet1") -> pd.DataFrame:
    """Load EVM workbook and return calculated metrics."""

    frame = pd.read_excel(path, sheet_name=sheet_name)
    return calculate_evm_metrics(frame)


def evm_summary(metrics: pd.DataFrame) -> dict[str, float | str | int]:
    """Return executive-level EVM summary metrics."""

    latest = metrics.iloc[-1]
    return {
        "periods": int(len(metrics)),
        "latest_period": str(latest["time_period"]),
        "latest_cpi": round(float(latest["cost_performance_index"]), 4),
        "latest_spi": round(float(latest["schedule_performance_index"]), 4),
        "latest_cost_variance": round(float(latest["cost_variance"]), 2),
        "latest_schedule_variance": round(float(latest["schedule_variance"]), 2),
        "latest_status": str(latest["status"]),
    }
