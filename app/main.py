"""FastAPI application for Aerospace Quality Risk Analytics."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from app.evm_engine import evm_summary, load_evm_workbook
from app.risk_engine import Risk, default_risk_register, score_risk, summarize_risks
from app.schemas import EVMMetrics, RiskInput, RiskScore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBOOK_PATH = PROJECT_ROOT / "data" / "raw" / "evm_data.xlsx"

app = FastAPI(
    title="Aerospace Quality Risk Analytics API",
    version="1.0.0",
    description=(
        "Portfolio-ready API that modernizes an academic Boeing 737 MAX quality "
        "analysis into risk scoring, EVM analytics, and quality-control metrics."
    ),
)


@app.get("/health")
def health() -> dict[str, str]:
    """Health endpoint for local checks and deployment probes."""

    return {"status": "ok"}


@app.get("/risks")
def get_risks() -> list[dict[str, object]]:
    """Return the default aerospace risk register with calculated scores."""

    return [score_risk(risk) for risk in default_risk_register()]


@app.get("/risks/summary")
def get_risk_summary() -> dict[str, object]:
    """Return aggregate risk metrics."""

    return summarize_risks(default_risk_register())


@app.post("/risks/score", response_model=RiskScore)
def post_risk_score(payload: RiskInput) -> dict[str, object]:
    """Score a user-provided risk item."""

    risk = Risk(
        risk_id=payload.risk_id,
        title=payload.title,
        category=payload.category.value,
        probability=payload.probability,
        impact=payload.impact,
        detectability=payload.detectability or 3,
        mitigation=payload.mitigation,
    )
    return score_risk(risk)


@app.get("/evm", response_model=list[EVMMetrics])
def get_evm_metrics(
    sheet_name: str = Query(default="Sheet1", description="Excel sheet to analyze")
) -> list[dict[str, object]]:
    """Return calculated EVM metrics from the original workbook."""

    try:
        metrics = load_evm_workbook(WORKBOOK_PATH, sheet_name=sheet_name)
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return metrics.round(4).to_dict(orient="records")


@app.get("/evm/summary")
def get_evm_summary(
    sheet_name: str = Query(default="Sheet1", description="Excel sheet to summarize")
) -> dict[str, float | str | int]:
    """Return executive summary for EVM performance."""

    try:
        metrics = load_evm_workbook(WORKBOOK_PATH, sheet_name=sheet_name)
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return evm_summary(metrics)
