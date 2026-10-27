"""Cleaning functions for messy, multi-source real-world data: tutoring
session logs, website analytics, and SEO keyword data."""
from __future__ import annotations

import pandas as pd

SUBJECT_ALIASES = {
    "math": "Math",
    "mathematics": "Math",
    "reading": "Reading",
    "science": "Science",
    "sci": "Science",
    "writing": "Writing",
}

DURATION_MIN_MINUTES = 10
DURATION_MAX_MINUTES = 120


def standardize_subject(raw_subject: str) -> str:
    """Map any known spelling/casing variant to its canonical subject name;
    unrecognized values fall back to title case rather than being dropped."""
    key = raw_subject.strip().lower()
    return SUBJECT_ALIASES.get(key, raw_subject.strip().title())


def clean_sessions(df: pd.DataFrame) -> pd.DataFrame:
    """Dedupe, standardize subject spelling, flag and clip duration
    outliers, and impute missing engagement ratings per subject."""
    cleaned = df.drop_duplicates().copy()
    cleaned["subject"] = cleaned["subject"].map(standardize_subject)

    cleaned["duration_outlier"] = (
        (cleaned["duration_minutes"] < DURATION_MIN_MINUTES)
        | (cleaned["duration_minutes"] > DURATION_MAX_MINUTES)
    )
    cleaned["duration_minutes"] = cleaned["duration_minutes"].clip(
        lower=DURATION_MIN_MINUTES, upper=DURATION_MAX_MINUTES
    )

    cleaned["engagement_rating"] = cleaned.groupby("subject")["engagement_rating"].transform(
        lambda s: s.fillna(s.median())
    )

    cleaned["pre_assessment_score"] = cleaned["pre_assessment_score"].clip(lower=0, upper=100)
    cleaned["post_assessment_score"] = cleaned["post_assessment_score"].clip(lower=0, upper=100)

    return cleaned.reset_index(drop=True)


def clean_web_analytics(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize source/medium casing and fill missing bounce rates with
    the per-source median rather than dropping incomplete rows."""
    cleaned = df.copy()
    cleaned["source_medium"] = cleaned["source_medium"].str.strip().str.lower()
    cleaned["bounce_rate"] = cleaned.groupby("source_medium")["bounce_rate"].transform(
        lambda s: s.fillna(s.median())
    )
    for column in ("sessions", "pageviews", "conversions"):
        cleaned[column] = cleaned[column].clip(lower=0)
    return cleaned


def clean_keyword_data(df: pd.DataFrame) -> pd.DataFrame:
    """Keyword data where a missing ranking genuinely means "not yet
    ranked" -- so it is labeled explicitly rather than imputed."""
    cleaned = df.copy()
    cleaned["keyword"] = cleaned["keyword"].str.strip().str.lower()
    cleaned["is_ranked"] = cleaned["current_ranking"].notna()
    return cleaned
