"""Marketing and web analytics helpers: conversion rate by acquisition
source, SEO keyword opportunity scoring, and a rolling traffic trend."""
from __future__ import annotations

import pandas as pd


def conversion_rate_by_source(cleaned_web: pd.DataFrame) -> pd.DataFrame:
    grouped = cleaned_web.groupby("source_medium").agg(
        total_sessions=("sessions", "sum"),
        total_conversions=("conversions", "sum"),
        avg_bounce_rate=("bounce_rate", "mean"),
    )
    grouped["conversion_rate"] = grouped["total_conversions"] / grouped["total_sessions"]
    return grouped.reset_index().sort_values("conversion_rate", ascending=False)


def keyword_opportunities(cleaned_keywords: pd.DataFrame, ranking_threshold: int = 20) -> pd.DataFrame:
    """A keyword is a bigger opportunity the higher its search volume and
    the worse (or absent) its current ranking -- an unranked high-volume
    keyword scores highest."""
    opportunities = cleaned_keywords.copy()

    def _opportunity(row: pd.Series) -> float:
        if not row["is_ranked"]:
            return float(row["search_volume"])
        ranking_gap = max(0.0, row["current_ranking"] - ranking_threshold)
        return row["search_volume"] * (ranking_gap / 100)

    opportunities["opportunity_score"] = opportunities.apply(_opportunity, axis=1)
    return opportunities.sort_values("opportunity_score", ascending=False).reset_index(drop=True)


def traffic_trend(cleaned_web: pd.DataFrame) -> pd.DataFrame:
    daily = (
        cleaned_web.groupby("date")
        .agg(total_sessions=("sessions", "sum"), total_conversions=("conversions", "sum"))
        .reset_index()
        .sort_values("date")
    )
    daily["seven_day_avg_sessions"] = daily["total_sessions"].rolling(7, min_periods=1).mean()
    return daily.reset_index(drop=True)
