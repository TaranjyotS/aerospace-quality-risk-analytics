"""Pydantic schemas for the Aerospace Quality Risk Analytics API."""

from enum import Enum

from pydantic import BaseModel, Field


class RiskCategory(str, Enum):
    """Supported quality and project risk categories."""

    DESIGN = "Design"
    SAFETY = "Safety"
    PROCESS = "Process"
    COMPLIANCE = "Compliance"
    SUPPLY_CHAIN = "Supply Chain"
    PROJECT = "Project"


class RiskInput(BaseModel):
    """Input contract for risk scoring."""

    risk_id: str = Field(..., examples=["R-001"])
    title: str = Field(..., examples=["Sensor redundancy gap"])
    category: RiskCategory
    probability: int = Field(..., ge=1, le=5, description="1=rare, 5=almost certain")
    impact: int = Field(..., ge=1, le=5, description="1=low, 5=critical")
    detectability: int | None = Field(
        default=3,
        ge=1,
        le=5,
        description="1=easy to detect, 5=difficult to detect",
    )
    mitigation: str | None = None


class RiskScore(BaseModel):
    """Risk scoring response."""

    risk_id: str
    title: str
    category: RiskCategory
    probability: int
    impact: int
    detectability: int
    risk_score: int
    risk_priority_number: int
    severity: str
    mitigation: str | None


class EVMMetrics(BaseModel):
    """Earned Value Management metrics for one time period."""

    time_period: str
    cost: float
    planned_value: float
    actual_cost: float
    earned_value: float
    cost_variance: float
    schedule_variance: float
    cost_performance_index: float
    schedule_performance_index: float
    status: str
