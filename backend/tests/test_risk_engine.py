from app.services.risk_engine import calculate_risk, risk_level, normalize


def test_healthy_drive_is_low():
    score, level = calculate_risk(35, 0, 5000, 5)
    assert level == "LOW" and score < 0.4


def test_failing_drive_is_high():
    score, level = calculate_risk(62, 400, 50000, 80)
    assert level == "HIGH" and score >= 0.7


def test_score_is_capped_at_one():
    score, _ = calculate_risk(500, 10**6, 10**7, 10**4)
    assert score == 1.0


def test_thresholds():
    assert risk_level(0.39) == "LOW"
    assert risk_level(0.40) == "MEDIUM"
    assert risk_level(0.69) == "MEDIUM"
    assert risk_level(0.70) == "HIGH"


def test_normalize_clamps():
    assert normalize(-5, 0, 10) == 0 and normalize(50, 0, 10) == 1
