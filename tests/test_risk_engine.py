from app.risk_engine import Risk, classify_severity, score_risk, summarize_risks


def test_classify_severity_boundaries():
    assert classify_severity(25) == "Critical"
    assert classify_severity(12) == "High"
    assert classify_severity(6) == "Medium"
    assert classify_severity(1) == "Low"


def test_score_risk_calculates_score_and_rpn():
    risk = Risk(
        "R-100",
        "Test risk",
        "Design",
        probability=4,
        impact=5,
        detectability=3,
    )
    result = score_risk(risk)
    assert result["risk_score"] == 20
    assert result["risk_priority_number"] == 60
    assert result["severity"] == "Critical"


def test_summarize_risks_returns_top_risk():
    risks = [
        Risk("R-1", "Low", "Project", 1, 2, 2),
        Risk("R-2", "High", "Safety", 5, 5, 5),
    ]
    summary = summarize_risks(risks)
    assert summary["total_risks"] == 2
    assert summary["top_risk"]["risk_id"] == "R-2"
