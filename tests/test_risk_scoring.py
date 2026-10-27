import pandas as pd

from app.risk_scoring import score_students


def _session_rows(student_id, pre_scores, engagement):
    rows = []
    for i, pre in enumerate(pre_scores):
        rows.append({
            "student_id": student_id,
            "session_date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=i * 7),
            "subject": "Math",
            "pre_assessment_score": pre,
            "post_assessment_score": pre + 5,
            "engagement_rating": engagement,
        })
    return rows


def test_high_performing_improving_student_scores_low_risk():
    df = pd.DataFrame(_session_rows("S001", [80, 83, 86, 90], engagement=5))
    result = score_students(df)
    row = result.iloc[0]
    assert row["category"] == "on_track"
    assert row["risk_score"] < 40


def test_struggling_declining_student_scores_high_risk():
    df = pd.DataFrame(_session_rows("S002", [50, 46, 42, 38], engagement=1))
    result = score_students(df)
    row = result.iloc[0]
    assert row["category"] == "needs_support"
    assert row["risk_score"] >= 60


def test_single_session_student_has_zero_trend():
    df = pd.DataFrame(_session_rows("S003", [70], engagement=3))
    result = score_students(df)
    assert result.iloc[0]["score_trend"] == 0.0


def test_scores_multiple_students_independently():
    df = pd.DataFrame(
        _session_rows("S001", [80, 85, 90], engagement=5)
        + _session_rows("S002", [50, 45, 40], engagement=1)
    )
    result = score_students(df).set_index("student_id")
    assert result.loc["S001", "risk_score"] < result.loc["S002", "risk_score"]
