"""A transparent, explainable academic-need scoring model: turns per-student
session history into a single risk score used to flag students who may need
additional support, synthesizing performance level, trend, and engagement."""
from __future__ import annotations

import numpy as np
import pandas as pd

NEEDS_SUPPORT_THRESHOLD = 60
MONITOR_THRESHOLD = 40

PERFORMANCE_WEIGHT = 0.4
TREND_WEIGHT = 0.3
ENGAGEMENT_WEIGHT = 0.3


def _score_trend(scores: pd.Series) -> float:
    """Slope of pre-assessment score across sessions; 0 if too few points
    to fit a trend line."""
    if len(scores) < 2:
        return 0.0
    x = np.arange(len(scores))
    slope, _ = np.polyfit(x, scores.to_numpy(), 1)
    return float(slope)


def score_students(cleaned_sessions: pd.DataFrame) -> pd.DataFrame:
    """One row per student: average pre-assessment score, score trend,
    average engagement, a 0-100 risk score, and a support category."""
    rows = []
    for student_id, group in cleaned_sessions.sort_values("session_date").groupby("student_id"):
        avg_pre = group["pre_assessment_score"].mean()
        trend = _score_trend(group["pre_assessment_score"])
        avg_engagement = group["engagement_rating"].mean()

        performance_component = avg_pre
        trend_component = min(100.0, max(0.0, 50 + trend * 10))
        engagement_component = (avg_engagement / 5) * 100

        composite = (
            PERFORMANCE_WEIGHT * performance_component
            + TREND_WEIGHT * trend_component
            + ENGAGEMENT_WEIGHT * engagement_component
        )
        risk_score = round(100 - composite, 1)

        if risk_score >= NEEDS_SUPPORT_THRESHOLD:
            category = "needs_support"
        elif risk_score >= MONITOR_THRESHOLD:
            category = "monitor"
        else:
            category = "on_track"

        rows.append({
            "student_id": student_id,
            "avg_pre_score": round(avg_pre, 1),
            "score_trend": round(trend, 2),
            "avg_engagement": round(avg_engagement, 2),
            "risk_score": risk_score,
            "category": category,
        })

    return pd.DataFrame(rows)
