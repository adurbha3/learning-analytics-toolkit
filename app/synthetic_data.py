"""Synthetic, seeded, deliberately messy multi-source data: tutoring session
logs, website analytics, and SEO keyword data, mirroring the kind of
real-world mess a small edtech company actually has to clean."""
from __future__ import annotations

import numpy as np
import pandas as pd

SUBJECTS = ["Math", "Reading", "Science", "Writing"]
SUBJECT_SPELLINGS = {
    "Math": ["Math", "math", "MATH", "Mathematics"],
    "Reading": ["Reading", "reading", "READING"],
    "Science": ["Science", "science", "SCI"],
    "Writing": ["Writing", "writing", "WRITING"],
}
SOURCES = ["google / organic", "facebook / cpc", "instagram / social", "direct / none", "newsletter / email"]
KEYWORDS = [
    "online tutoring for kids", "math tutor near me", "sat prep online",
    "reading comprehension help", "science tutor for middle school",
    "best tutoring service", "writing tutor online", "act prep course",
    "homework help website", "personalized tutoring",
]


def generate_sessions(n_students: int = 40, sessions_per_student: int = 6, seed: int = 0) -> pd.DataFrame:
    """Tutoring session logs with inconsistent subject spellings, a few
    missing engagement ratings, a few duplicate rows, and a few duration
    outliers -- the kind of mess real session-tracking data actually has."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_students):
        student_id = f"S{i + 1:03d}"
        true_subject = rng.choice(SUBJECTS)
        base_score = rng.uniform(40, 75)
        improvement_rate = rng.uniform(-2, 6)
        for session_num in range(sessions_per_student):
            spelling = rng.choice(SUBJECT_SPELLINGS[true_subject])
            duration = rng.normal(45, 10)
            if rng.random() < 0.03:
                duration *= 5
            pre_score = min(100, max(0, base_score + improvement_rate * session_num + rng.normal(0, 3)))
            post_score = min(100, max(0, pre_score + rng.uniform(0, 8)))
            engagement = rng.integers(1, 6)
            rows.append({
                "student_id": student_id,
                "session_date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=session_num * 7 + i),
                "subject": spelling,
                "tutor_id": f"T{rng.integers(1, 9):02d}",
                "duration_minutes": round(duration, 1),
                "pre_assessment_score": round(pre_score, 1),
                "post_assessment_score": round(post_score, 1),
                "engagement_rating": int(engagement) if rng.random() > 0.05 else np.nan,
            })

    df = pd.DataFrame(rows)
    duplicate_rows = df.sample(n=max(1, len(df) // 25), random_state=seed)
    return pd.concat([df, duplicate_rows], ignore_index=True)


def generate_web_analytics(n_days: int = 60, seed: int = 1) -> pd.DataFrame:
    """Daily website analytics by source/medium, GA4-style, with a few
    missing bounce rates and inconsistent source/medium casing."""
    rng = np.random.default_rng(seed)
    rows = []
    for day in range(n_days):
        date = pd.Timestamp("2026-01-01") + pd.Timedelta(days=day)
        for source in SOURCES:
            base_sessions = {"google / organic": 120, "facebook / cpc": 60, "instagram / social": 40,
                              "direct / none": 50, "newsletter / email": 20}[source]
            sessions = max(0, int(rng.normal(base_sessions, base_sessions * 0.2)))
            pageviews = int(sessions * rng.uniform(1.5, 3.0))
            conversions = int(sessions * rng.uniform(0.01, 0.06))
            bounce_rate = rng.uniform(0.2, 0.7)
            source_label = source.upper() if rng.random() < 0.1 else source
            rows.append({
                "date": date,
                "source_medium": source_label,
                "sessions": sessions,
                "pageviews": pageviews,
                "conversions": conversions,
                "bounce_rate": round(bounce_rate, 3) if rng.random() > 0.04 else np.nan,
            })
    return pd.DataFrame(rows)


def generate_keyword_data(seed: int = 2) -> pd.DataFrame:
    """SEO keyword research data: search volume, current ranking (missing
    means not yet ranked), and click-through rate."""
    rng = np.random.default_rng(seed)
    rows = []
    for keyword in KEYWORDS:
        search_volume = int(rng.integers(200, 8000))
        ranked = rng.random() > 0.2
        current_ranking = int(rng.integers(1, 100)) if ranked else np.nan
        click_through_rate = round(rng.uniform(0.01, 0.12), 3) if ranked else np.nan
        rows.append({
            "keyword": keyword,
            "search_volume": search_volume,
            "current_ranking": current_ranking,
            "click_through_rate": click_through_rate,
            "campaign": "organic" if ranked else "unranked",
        })
    return pd.DataFrame(rows)
