"""
Reusable feature store: central functions that turn cleaned session-level
xDR rows into per-user (MSISDN) feature tables. Every task (overview,
engagement, experience, satisfaction) and the dashboard pull from these same
functions so metric definitions never drift between notebooks / scripts.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data_prep import APP_COLUMNS

USER_ID_COL = "MSISDN/Number"


def get_user_overview_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-user aggregation for Task 1: session count, total session duration,
    total DL/UL, and total data volume per tracked application.
    """
    agg = {
        "Bearer Id": "count",
        "Dur. (ms)": "sum",
        "Total DL (Bytes)": "sum",
        "Total UL (Bytes)": "sum",
    }
    for app in APP_COLUMNS:
        dl, ul = f"{app} DL (Bytes)", f"{app} UL (Bytes)"
        if dl in df.columns:
            agg[dl] = "sum"
        if ul in df.columns:
            agg[ul] = "sum"

    features = df.groupby(USER_ID_COL).agg(agg).rename(
        columns={"Bearer Id": "xdr_sessions", "Dur. (ms)": "total_duration_ms"}
    )
    features["total_data_bytes"] = (
        features["Total DL (Bytes)"] + features["Total UL (Bytes)"]
    )
    for app in APP_COLUMNS:
        dl, ul = f"{app} DL (Bytes)", f"{app} UL (Bytes)"
        if dl in features.columns and ul in features.columns:
            features[f"{app}_total_bytes"] = features[dl] + features[ul]
    return features.reset_index()


def get_user_engagement_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-user engagement metrics for Task 2: session frequency, total
    session duration, and total session traffic (DL+UL bytes).
    """
    features = df.groupby(USER_ID_COL).agg(
        sessions_frequency=("Bearer Id", "count"),
        total_duration_ms=("Dur. (ms)", "sum"),
        total_dl_bytes=("Total DL (Bytes)", "sum"),
        total_ul_bytes=("Total UL (Bytes)", "sum"),
    )
    features["total_traffic_bytes"] = (
        features["total_dl_bytes"] + features["total_ul_bytes"]
    )
    return features.reset_index()


def get_user_experience_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-user experience metrics for Task 3: average TCP retransmission,
    average RTT, average throughput, and (most frequent) handset type.
    """
    def _mode_or_nan(s: pd.Series):
        m = s.mode(dropna=True)
        return m.iloc[0] if len(m) else np.nan

    features = df.groupby(USER_ID_COL).agg(
        avg_tcp_retrans_bytes=(
            "TCP DL Retrans. Vol (Bytes)", "mean"
        ),
        avg_tcp_retrans_ul_bytes=(
            "TCP UL Retrans. Vol (Bytes)", "mean"
        ),
        avg_rtt_dl_ms=("Avg RTT DL (ms)", "mean"),
        avg_rtt_ul_ms=("Avg RTT UL (ms)", "mean"),
        avg_throughput_dl_kbps=("Avg Bearer TP DL (kbps)", "mean"),
        avg_throughput_ul_kbps=("Avg Bearer TP UL (kbps)", "mean"),
    )
    handset = df.groupby(USER_ID_COL)["Handset Type"].agg(_mode_or_nan)
    features["handset_type"] = handset
    features["avg_tcp_retrans_total_bytes"] = (
        features["avg_tcp_retrans_bytes"].fillna(0)
        + features["avg_tcp_retrans_ul_bytes"].fillna(0)
    )
    features["avg_rtt_ms"] = (
        features["avg_rtt_dl_ms"].fillna(0) + features["avg_rtt_ul_ms"].fillna(0)
    )
    features["avg_throughput_kbps"] = (
        features["avg_throughput_dl_kbps"].fillna(0)
        + features["avg_throughput_ul_kbps"].fillna(0)
    )
    return features.reset_index()
