import pandas as pd

from app.marketing_analytics import conversion_rate_by_source, keyword_opportunities, traffic_trend


def test_conversion_rate_by_source_computes_correctly():
    df = pd.DataFrame([
        {"date": pd.Timestamp("2026-01-01"), "source_medium": "google / organic", "sessions": 100,
         "pageviews": 200, "conversions": 10, "bounce_rate": 0.3},
        {"date": pd.Timestamp("2026-01-02"), "source_medium": "google / organic", "sessions": 100,
         "pageviews": 200, "conversions": 10, "bounce_rate": 0.3},
        {"date": pd.Timestamp("2026-01-01"), "source_medium": "facebook / cpc", "sessions": 100,
         "pageviews": 150, "conversions": 2, "bounce_rate": 0.6},
    ])
    result = conversion_rate_by_source(df).set_index("source_medium")
    assert result.loc["google / organic", "conversion_rate"] == 0.1
    assert result.loc["facebook / cpc", "conversion_rate"] == 0.02
    # sorted descending by conversion rate
    assert conversion_rate_by_source(df).iloc[0]["source_medium"] == "google / organic"


def test_keyword_opportunities_ranks_unranked_high_volume_first():
    df = pd.DataFrame([
        {"keyword": "a", "search_volume": 5000, "current_ranking": None, "click_through_rate": None,
         "is_ranked": False},
        {"keyword": "b", "search_volume": 100, "current_ranking": 3, "click_through_rate": 0.1,
         "is_ranked": True},
    ])
    result = keyword_opportunities(df)
    assert result.iloc[0]["keyword"] == "a"


def test_keyword_opportunities_penalizes_well_ranked_keywords():
    df = pd.DataFrame([
        {"keyword": "well-ranked", "search_volume": 5000, "current_ranking": 1,
         "click_through_rate": 0.2, "is_ranked": True},
        {"keyword": "poorly-ranked", "search_volume": 5000, "current_ranking": 90,
         "click_through_rate": 0.01, "is_ranked": True},
    ])
    result = keyword_opportunities(df).set_index("keyword")
    assert result.loc["poorly-ranked", "opportunity_score"] > result.loc["well-ranked", "opportunity_score"]


def test_traffic_trend_computes_rolling_average():
    df = pd.DataFrame([
        {"date": pd.Timestamp("2026-01-01"), "sessions": 100, "conversions": 5},
        {"date": pd.Timestamp("2026-01-01"), "sessions": 50, "conversions": 2},
        {"date": pd.Timestamp("2026-01-02"), "sessions": 200, "conversions": 10},
    ])
    result = traffic_trend(df)
    assert list(result["total_sessions"]) == [150, 200]
    assert result.iloc[0]["seven_day_avg_sessions"] == 150
    assert result.iloc[1]["seven_day_avg_sessions"] == 175
