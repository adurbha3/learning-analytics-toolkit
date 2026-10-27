import numpy as np
import pandas as pd
import pytest

from app.cleaning import clean_keyword_data, clean_sessions, clean_web_analytics, standardize_subject


def test_standardize_subject_maps_known_variants():
    assert standardize_subject("MATH") == "Math"
    assert standardize_subject("mathematics") == "Math"
    assert standardize_subject("  Reading ") == "Reading"
    assert standardize_subject("SCI") == "Science"


def test_standardize_subject_falls_back_to_title_case_for_unknown():
    assert standardize_subject("history") == "History"


def test_clean_sessions_removes_exact_duplicates():
    row = {
        "student_id": "S001", "session_date": pd.Timestamp("2026-01-01"), "subject": "Math",
        "tutor_id": "T01", "duration_minutes": 45.0, "pre_assessment_score": 70.0,
        "post_assessment_score": 75.0, "engagement_rating": 4,
    }
    df = pd.DataFrame([row, row, row])
    cleaned = clean_sessions(df)
    assert len(cleaned) == 1


def test_clean_sessions_standardizes_subject_spelling():
    df = pd.DataFrame([
        {"student_id": "S001", "session_date": pd.Timestamp("2026-01-01"), "subject": "MATH",
         "tutor_id": "T01", "duration_minutes": 45.0, "pre_assessment_score": 70.0,
         "post_assessment_score": 75.0, "engagement_rating": 4},
        {"student_id": "S001", "session_date": pd.Timestamp("2026-01-08"), "subject": "mathematics",
         "tutor_id": "T01", "duration_minutes": 40.0, "pre_assessment_score": 72.0,
         "post_assessment_score": 78.0, "engagement_rating": 3},
    ])
    cleaned = clean_sessions(df)
    assert set(cleaned["subject"]) == {"Math"}


def test_clean_sessions_flags_and_clips_duration_outliers():
    df = pd.DataFrame([
        {"student_id": "S001", "session_date": pd.Timestamp("2026-01-01"), "subject": "Math",
         "tutor_id": "T01", "duration_minutes": 500.0, "pre_assessment_score": 70.0,
         "post_assessment_score": 75.0, "engagement_rating": 4},
    ])
    cleaned = clean_sessions(df)
    assert cleaned.loc[0, "duration_outlier"] is np.True_ or cleaned.loc[0, "duration_outlier"] is True
    assert cleaned.loc[0, "duration_minutes"] == 120


def test_clean_sessions_imputes_missing_engagement_with_subject_median():
    df = pd.DataFrame([
        {"student_id": "S001", "session_date": pd.Timestamp("2026-01-01"), "subject": "Math",
         "tutor_id": "T01", "duration_minutes": 45.0, "pre_assessment_score": 70.0,
         "post_assessment_score": 75.0, "engagement_rating": 2},
        {"student_id": "S002", "session_date": pd.Timestamp("2026-01-01"), "subject": "Math",
         "tutor_id": "T01", "duration_minutes": 45.0, "pre_assessment_score": 70.0,
         "post_assessment_score": 75.0, "engagement_rating": 4},
        {"student_id": "S003", "session_date": pd.Timestamp("2026-01-01"), "subject": "Math",
         "tutor_id": "T01", "duration_minutes": 45.0, "pre_assessment_score": 70.0,
         "post_assessment_score": 75.0, "engagement_rating": np.nan},
    ])
    cleaned = clean_sessions(df)
    assert cleaned.loc[2, "engagement_rating"] == 3.0  # median of [2, 4]


def test_clean_web_analytics_normalizes_casing():
    df = pd.DataFrame([
        {"date": pd.Timestamp("2026-01-01"), "source_medium": "GOOGLE / ORGANIC", "sessions": 10,
         "pageviews": 20, "conversions": 1, "bounce_rate": 0.3},
        {"date": pd.Timestamp("2026-01-02"), "source_medium": "google / organic", "sessions": 12,
         "pageviews": 24, "conversions": 2, "bounce_rate": 0.4},
    ])
    cleaned = clean_web_analytics(df)
    assert set(cleaned["source_medium"]) == {"google / organic"}


def test_clean_web_analytics_fills_missing_bounce_rate_with_source_median():
    df = pd.DataFrame([
        {"date": pd.Timestamp("2026-01-01"), "source_medium": "direct / none", "sessions": 10,
         "pageviews": 20, "conversions": 1, "bounce_rate": 0.2},
        {"date": pd.Timestamp("2026-01-02"), "source_medium": "direct / none", "sessions": 10,
         "pageviews": 20, "conversions": 1, "bounce_rate": 0.4},
        {"date": pd.Timestamp("2026-01-03"), "source_medium": "direct / none", "sessions": 10,
         "pageviews": 20, "conversions": 1, "bounce_rate": np.nan},
    ])
    cleaned = clean_web_analytics(df)
    assert cleaned.loc[2, "bounce_rate"] == pytest.approx(0.3)


def test_clean_keyword_data_flags_ranked_vs_unranked():
    df = pd.DataFrame([
        {"keyword": "Math Tutor", "search_volume": 1000, "current_ranking": 5,
         "click_through_rate": 0.1, "campaign": "organic"},
        {"keyword": "SAT Prep", "search_volume": 2000, "current_ranking": np.nan,
         "click_through_rate": np.nan, "campaign": "unranked"},
    ])
    cleaned = clean_keyword_data(df)
    assert cleaned.loc[0, "is_ranked"]
    assert not cleaned.loc[1, "is_ranked"]
    assert cleaned.loc[0, "keyword"] == "math tutor"
