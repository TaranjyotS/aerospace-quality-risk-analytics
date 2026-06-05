"""Risk scoring utilities for aerospace quality and project controls.

The original Masters project used qualitative risk planning, a probability-impact
matrix, and quality control concepts. This module converts those ideas into a
small reusable scoring engine suitable for API, dashboard, and tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Risk:
    """A single project or product-quality risk."""

    risk_id: str
    title: str
    category: str
    probability: int
    impact: int
    detectability: int = 3
    mitigation: str | None = None


def classify_severity(score: int) -> str:
    """Classify a probability-impact score into portfolio-friendly severity."""

    if score >= 20:
        return "Critical"
    if score >= 12:
        return "High"
    if score >= 6:
        return "Medium"
    return "Low"


def score_risk(risk: Risk) -> dict[str, object]:
    """Calculate risk score and risk-priority number.

    Risk score follows the project report's probability-impact matrix concept.
    Risk Priority Number extends it with detectability, similar to FMEA-style
    quality analysis.
    """

    risk_score = risk.probability * risk.impact
    rpn = risk.probability * risk.impact * risk.detectability
    return {
        "risk_id": risk.risk_id,
        "title": risk.title,
        "category": risk.category,
        "probability": risk.probability,
        "impact": risk.impact,
        "detectability": risk.detectability,
        "risk_score": risk_score,
        "risk_priority_number": rpn,
        "severity": classify_severity(risk_score),
        "mitigation": risk.mitigation,
    }


def default_risk_register() -> list[Risk]:
    """Return a curated risk register based on the original project intent."""

    return [
        Risk(
            "R-001",
            "Single sensor dependency in safety-critical automation",
            "Design",
            4,
            5,
            4,
            "Introduce redundancy, cross-checking, and independent validation.",
        ),
        Risk(
            "R-002",
            "Incomplete hazard communication to pilots and operators",
            "Safety",
            3,
            5,
            4,
            "Improve documentation, simulator coverage, and change communication.",
        ),
        Risk(
            "R-003",
            "Schedule pressure reducing design review depth",
            "Project",
            4,
            4,
            3,
            "Add safety gates, design review checklists, and release criteria.",
        ),
        Risk(
            "R-004",
            "Regulatory approval dependency and certification ambiguity",
            "Compliance",
            3,
            5,
            3,
            "Maintain traceability, audit evidence, and independent compliance review.",
        ),
        Risk(
            "R-005",
            "Weak feedback loop between field incidents and corrective action",
            "Process",
            3,
            4,
            3,
            "Create closed-loop CAPA workflow with measurable ownership.",
        ),
    ]


def summarize_risks(risks: list[Risk]) -> dict[str, object]:
    """Aggregate risk register metrics for dashboards."""

    scored = [score_risk(risk) for risk in risks]
    severity_counts: dict[str, int] = {}
    for item in scored:
        severity = str(item["severity"])
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    top_risk = max(scored, key=lambda item: int(item["risk_priority_number"]))
    return {
        "total_risks": len(scored),
        "severity_counts": severity_counts,
        "average_risk_score": round(
            sum(int(item["risk_score"]) for item in scored) / len(scored), 2
        ),
        "top_risk": top_risk,
        "risks": scored,
    }
