"""
Data loading, cleaning, and missing-value / outlier treatment for the TellCo
xDR dataset.

Design notes
------------
The raw export has 55 columns and ~150k session-level rows (one row per xDR
bearer session). Several network-quality columns (TCP retransmission, HTTP
bytes, per-throughput-bucket second counts) have 15-87% missingness -- these
are "not applicable" style gaps (e.g. no retransmission event occurred) rather
than random data loss, so mean/mode imputation is the assignment-mandated and
defensible choice: it keeps the row usable for aggregation without injecting
a  fabricated extreme value the way 0-filling would.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

APP_COLUMNS = [
    "Social Media",
    "Google",
    "Email",
    "Youtube",
    "Netflix",
    "Gaming",
    "Other",
]

NUMERIC_OUTLIER_CAP_COLUMNS = [
    "Dur. (ms)",
    "Avg RTT DL (ms)",
    "Avg RTT UL (ms)",
    "Avg Bearer TP DL (kbps)",
    "Avg Bearer TP UL (kbps)",
    "TCP DL Retrans. Vol (Bytes)",
    "TCP UL Retrans. Vol (Bytes)",
    "Total UL (Bytes)",
    "Total DL (Bytes)",
]


def load_raw(path: str = "data/telcom_data.csv") -> pd.DataFrame:
    """Load the raw xDR export (CSV, produced from the original xlsx)."""
    df = pd.read_csv(path, low_memory=False)
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["End"] = pd.to_datetime(df["End"], errors="coerce")
    return df


def _cap_outliers_iqr(series: pd.Series, k: float = 3.0) -> pd.Series:
    """Cap values beyond k * IQR from Q1/Q3 (Tukey's fences, k=3 -> 'extreme')."""
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return series.clip(lower=lower, upper=upper)


def treat_missing_and_outliers(
    df: pd.DataFrame,
    cap_outliers: bool = True,
) -> pd.DataFrame:
    """
    Replace missing values with the column mean (numeric) or mode
    (categorical), as mandated by the assignment brief, then optionally cap
    extreme outliers (|value - median| > 3*IQR) to the fence value so a
    handful of corrupted/extreme sessions don't dominate downstream means
    and cluster centroids.
    """
    out = df.copy()
    numeric_cols = out.select_dtypes(include=[np.number]).columns
    categorical_cols = out.select_dtypes(include=["object"]).columns

    for col in numeric_cols:
        if out[col].isna().any():
            out[col] = out[col].fillna(out[col].mean())

    for col in categorical_cols:
        if out[col].isna().any():
            mode = out[col].mode(dropna=True)
            if len(mode):
                out[col] = out[col].fillna(mode.iloc[0])

    if cap_outliers:
        for col in NUMERIC_OUTLIER_CAP_COLUMNS:
            if col in out.columns:
                out[col] = _cap_outliers_iqr(out[col])

    return out


def add_total_app_bytes(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'Total {App} (Bytes)' = DL + UL column for each tracked app."""
    out = df.copy()
    for app in APP_COLUMNS:
        dl_col, ul_col = f"{app} DL (Bytes)", f"{app} UL (Bytes)"
        if dl_col in out.columns and ul_col in out.columns:
            out[f"Total {app} (Bytes)"] = out[dl_col].fillna(0) + out[ul_col].fillna(0)
    return out


def prepare_dataset(path: str = "data/telcom_data.csv") -> pd.DataFrame:
    """One-call convenience: load -> clean -> enrich."""
    df = load_raw(path)
    df = treat_missing_and_outliers(df)
    df = add_total_app_bytes(df)
    return df
