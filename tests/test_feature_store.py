import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pandas as pd

from tellco.feature_store import (
    get_user_overview_features,
    get_user_engagement_features,
    get_user_experience_features,
)


def _toy_df():
    return pd.DataFrame({
        "MSISDN/Number": [1, 1, 2],
        "Bearer Id": [10, 11, 12],
        "Dur. (ms)": [100, 200, 300],
        "Total DL (Bytes)": [1000, 2000, 3000],
        "Total UL (Bytes)": [10, 20, 30],
        "Social Media DL (Bytes)": [5, 5, 5],
        "Social Media UL (Bytes)": [1, 1, 1],
        "TCP DL Retrans. Vol (Bytes)": [0, 100, 200],
        "TCP UL Retrans. Vol (Bytes)": [0, 10, 20],
        "Avg RTT DL (ms)": [10, 20, 30],
        "Avg RTT UL (ms)": [1, 2, 3],
        "Avg Bearer TP DL (kbps)": [50, 60, 70],
        "Avg Bearer TP UL (kbps)": [5, 6, 7],
        "Handset Type": ["A", "A", "B"],
    })


def test_overview_features_session_count_per_user():
    df = _toy_df()
    feats = get_user_overview_features(df)
    user1 = feats[feats["MSISDN/Number"] == 1].iloc[0]
    assert user1["xdr_sessions"] == 2
    assert user1["total_duration_ms"] == 300


def test_engagement_features_total_traffic():
    df = _toy_df()
    feats = get_user_engagement_features(df)
    user1 = feats[feats["MSISDN/Number"] == 1].iloc[0]
    assert user1["sessions_frequency"] == 2
    assert user1["total_traffic_bytes"] == (1000 + 2000) + (10 + 20)


def test_experience_features_handset_mode():
    df = _toy_df()
    feats = get_user_experience_features(df)
    user1 = feats[feats["MSISDN/Number"] == 1].iloc[0]
    assert user1["handset_type"] == "A"
    assert user1["avg_rtt_dl_ms"] == 15.0
