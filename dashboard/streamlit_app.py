"""Interactive Streamlit dashboard for Aerospace Quality Risk Analytics.

The dashboard keeps the original academic quality-management intent alive while
turning the static report/workbook into a portfolio-ready analytics interface.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.evm_engine import evm_summary, load_evm_workbook  # noqa: E402
from app.risk_engine import default_risk_register, summarize_risks  # noqa: E402

WORKBOOK_PATH = ROOT / "data" / "raw" / "evm_data.xlsx"
SEVERITY_ORDER = ["Low", "Medium", "High", "Critical"]


def _load_risk_frame() -> tuple[pd.DataFrame, dict[str, object]]:
    """Load the default risk register as a dataframe and summary dictionary."""

    summary = summarize_risks(default_risk_register())
    frame = pd.DataFrame(summary["risks"])
    frame["severity"] = pd.Categorical(
        frame["severity"], categories=SEVERITY_ORDER, ordered=True
    )
    return frame.sort_values("risk_priority_number", ascending=False), summary


def _load_evm_frame(sheet_name: str) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load calculated EVM metrics and executive summary."""

    metrics = load_evm_workbook(WORKBOOK_PATH, sheet_name=sheet_name)
    metrics["time_period"] = metrics["time_period"].astype(str)
    return metrics, evm_summary(metrics)


def _project_health(latest_cpi: float, latest_spi: float) -> str:
    """Return a simple executive project-health label from CPI/SPI."""

    if latest_cpi >= 1 and latest_spi >= 1:
        return "On Track"
    if latest_cpi < 0.98 and latest_spi < 0.98:
        return "Cost & Schedule Risk"
    if latest_cpi < 0.98:
        return "Cost Risk"
    if latest_spi < 0.98:
        return "Schedule Risk"
    return "Watch"


def _render_header() -> None:
    """Render the dashboard heading."""

    st.title("✈️ Aerospace Quality Risk Analytics")
    st.caption(
        "Production-style upgrade of a Masters quality engineering project: "
        "risk register, FMEA-style RPN, EVM metrics, and quality-control insights."
    )


def _render_kpis(risk_frame: pd.DataFrame, evm: dict[str, object]) -> None:
    """Render executive KPI cards."""

    critical_count = int((risk_frame["severity"] == "Critical").sum())
    high_count = int((risk_frame["severity"] == "High").sum())
    avg_risk = round(float(risk_frame["risk_score"].mean()), 2)
    latest_cpi = float(evm["latest_cpi"])
    latest_spi = float(evm["latest_spi"])

    cols = st.columns(6)
    cols[0].metric("Total Risks", len(risk_frame))
    cols[1].metric("Critical Risks", critical_count)
    cols[2].metric("High Risks", high_count)
    cols[3].metric("Avg Risk Score", avg_risk)
    cols[4].metric("Latest CPI", latest_cpi)
    cols[5].metric("Latest SPI", latest_spi)

    st.info(
        f"Project Health: **{_project_health(latest_cpi, latest_spi)}** | "
        f"Latest EVM Period: **{evm['latest_period']}**"
    )


def _render_risk_heatmap(risk_frame: pd.DataFrame) -> None:
    """Render a probability-impact heatmap from the selected risks."""

    heatmap = (
        risk_frame.pivot_table(
            index="impact",
            columns="probability",
            values="risk_id",
            aggfunc="count",
            fill_value=0,
            observed=False,
        )
        .reindex(index=[5, 4, 3, 2, 1], columns=[1, 2, 3, 4, 5], fill_value=0)
        .astype(int)
    )
    heatmap.index.name = "Impact"
    heatmap.columns.name = "Probability"

    st.dataframe(
        heatmap.style.background_gradient(axis=None),
        use_container_width=True,
    )


def _render_executive_summary(risk_frame: pd.DataFrame, evm: dict[str, object]) -> None:
    """Render the executive summary tab."""

    st.subheader("Executive Summary")
    st.write(
        "This dashboard converts the original report's quality-management concepts "
        "into measurable project controls: top risks, severity distribution, "
        "risk-priority numbers, and earned value management indicators."
    )

    top_risk = risk_frame.iloc[0]
    left, right = st.columns(2)
    with left:
        st.markdown("#### Highest Priority Risk")
        st.write(f"**{top_risk['risk_id']} — {top_risk['title']}**")
        st.write(f"Severity: **{top_risk['severity']}**")
        st.write(f"Risk Priority Number: **{top_risk['risk_priority_number']}**")
        st.write(f"Mitigation: {top_risk['mitigation']}")

    with right:
        st.markdown("#### EVM Snapshot")
        st.write(f"Latest period: **{evm['latest_period']}**")
        st.write(f"Latest status: **{evm['latest_status']}**")
        st.write(f"Cost variance: **{evm['latest_cost_variance']}**")
        st.write(f"Schedule variance: **{evm['latest_schedule_variance']}**")

    st.markdown("#### Risk Severity Distribution")
    severity_counts = risk_frame["severity"].value_counts().reindex(SEVERITY_ORDER)
    st.bar_chart(severity_counts.fillna(0))


def _render_risk_register(risk_frame: pd.DataFrame) -> None:
    """Render risk register, heatmap, and category summaries."""

    st.subheader("Risk Register")
    st.dataframe(risk_frame, use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    with left:
        st.markdown("#### Probability × Impact Heatmap")
        _render_risk_heatmap(risk_frame)
    with right:
        st.markdown("#### Risk Score by Category")
        category_scores = risk_frame.groupby(
            "category", observed=False
        )["risk_score"].mean()
        st.bar_chart(category_scores.sort_values(ascending=False))


def _render_evm_analytics(metrics: pd.DataFrame) -> None:
    """Render EVM details and trend charts."""

    st.subheader("Earned Value Management Analytics")
    st.dataframe(metrics.round(4), use_container_width=True, hide_index=True)

    trend_frame = metrics.set_index("time_period")[
        ["planned_value", "actual_cost", "earned_value"]
    ]
    st.markdown("#### PV / AC / EV Trend")
    st.line_chart(trend_frame)

    variance_frame = metrics.set_index("time_period")[
        ["cost_variance", "schedule_variance"]
    ]
    st.markdown("#### Cost and Schedule Variance")
    st.line_chart(variance_frame)


def _render_recommendations(risk_frame: pd.DataFrame) -> None:
    """Render prioritized mitigation recommendations."""

    st.subheader("Recommended Quality-Control Actions")
    st.write(
        "Prioritized recommendations are derived from the highest RPN items in the "
        "risk register. They preserve the original project theme while presenting "
        "it as an actionable engineering control system."
    )

    for _, row in risk_frame.head(5).iterrows():
        with st.expander(f"{row['risk_id']} — {row['title']}", expanded=False):
            st.write(f"**Category:** {row['category']}")
            st.write(f"**Severity:** {row['severity']}")
            st.write(f"**Risk Priority Number:** {row['risk_priority_number']}")
            st.write(f"**Mitigation:** {row['mitigation']}")

    st.markdown("#### Quality Engineering Controls")
    st.table(
        pd.DataFrame(
            [
                {
                    "Control Area": "Design Assurance",
                    "Recommended Action": (
                        "Independent safety review and redundancy checks"
                    ),
                },
                {
                    "Control Area": "Change Management",
                    "Recommended Action": (
                        "Traceable approval workflow for design changes"
                    ),
                },
                {
                    "Control Area": "CAPA",
                    "Recommended Action": (
                        "Closed-loop corrective action ownership and aging review"
                    ),
                },
                {
                    "Control Area": "Release Governance",
                    "Recommended Action": (
                        "Risk-based release gates and documented acceptance criteria"
                    ),
                },
            ]
        )
    )


def main() -> None:
    """Run the Streamlit dashboard."""

    st.set_page_config(
        page_title="Aerospace Quality Risk Analytics",
        page_icon="✈️",
        layout="wide",
    )

    risk_frame, _risk_summary = _load_risk_frame()
    metrics, evm = _load_evm_frame(sheet_name="Sheet1")

    st.sidebar.header("Analysis Controls")
    categories = sorted(risk_frame["category"].unique().tolist())
    severities = [
        item for item in SEVERITY_ORDER if item in risk_frame["severity"].unique()
    ]

    selected_categories = st.sidebar.multiselect(
        "Risk Category",
        options=categories,
        default=categories,
    )
    selected_severities = st.sidebar.multiselect(
        "Severity",
        options=severities,
        default=severities,
    )
    min_rpn = st.sidebar.slider(
        "Minimum Risk Priority Number",
        min_value=0,
        max_value=int(risk_frame["risk_priority_number"].max()),
        value=0,
    )

    filtered_risks = risk_frame[
        risk_frame["category"].isin(selected_categories)
        & risk_frame["severity"].isin(selected_severities)
        & (risk_frame["risk_priority_number"] >= min_rpn)
    ]

    _render_header()
    _render_kpis(filtered_risks, evm)

    tab_summary, tab_risks, tab_evm, tab_recommendations = st.tabs(
        [
            "📈 Executive Summary",
            "⚠️ Risk Register",
            "💰 EVM Analytics",
            "📋 Recommendations",
        ]
    )

    with tab_summary:
        _render_executive_summary(filtered_risks, evm)
    with tab_risks:
        _render_risk_register(filtered_risks)
    with tab_evm:
        _render_evm_analytics(metrics)
    with tab_recommendations:
        _render_recommendations(filtered_risks)


if __name__ == "__main__":
    main()
