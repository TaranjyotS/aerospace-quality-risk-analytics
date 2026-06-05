"""Quality-control metrics inspired by the original Boeing 737 MAX analysis."""

from __future__ import annotations


def defect_escape_rate(escaped_defects: int, total_defects: int) -> float:
    """Calculate the percentage of defects escaping internal controls."""

    if total_defects <= 0:
        raise ValueError("total_defects must be greater than zero")
    return round((escaped_defects / total_defects) * 100, 2)


def corrective_action_closure_rate(closed_actions: int, total_actions: int) -> float:
    """Calculate CAPA closure rate as a percentage."""

    if total_actions <= 0:
        raise ValueError("total_actions must be greater than zero")
    return round((closed_actions / total_actions) * 100, 2)


def audit_findings_density(findings: int, audit_hours: float) -> float:
    """Calculate findings per audit hour."""

    if audit_hours <= 0:
        raise ValueError("audit_hours must be greater than zero")
    return round(findings / audit_hours, 2)
