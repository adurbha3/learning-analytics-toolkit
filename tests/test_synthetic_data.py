from app.synthetic_data import generate_keyword_data, generate_sessions, generate_web_analytics


def test_generate_sessions_reproducible_with_same_seed():
    a = generate_sessions(n_students=5, sessions_per_student=3, seed=7)
    b = generate_sessions(n_students=5, sessions_per_student=3, seed=7)
    assert a.equals(b)


def test_generate_sessions_includes_injected_duplicates():
    df = generate_sessions(n_students=20, sessions_per_student=6, seed=0)
    assert df.duplicated().sum() > 0


def test_generate_sessions_includes_subject_spelling_variants():
    df = generate_sessions(n_students=20, sessions_per_student=6, seed=0)
    assert df["subject"].nunique() > 4  # more spellings than actual subjects


def test_generate_web_analytics_shape():
    df = generate_web_analytics(n_days=10, seed=1)
    assert len(df) == 10 * 5  # 5 sources per day
    assert df["bounce_rate"].isna().sum() > 0


def test_generate_keyword_data_unranked_rows_have_nan_ranking():
    df = generate_keyword_data(seed=2)
    unranked = df[df["campaign"] == "unranked"]
    assert unranked["current_ranking"].isna().all()
    ranked = df[df["campaign"] == "organic"]
    assert ranked["current_ranking"].notna().all()
