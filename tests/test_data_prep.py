import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
import pytest

from tellco.data_prep import treat_missing_and_outliers, add_total_app_bytes, APP_COLUMNS


@pytest.fixture
def sample_df():
    # 20 "normal" rows clustered around 100-300ms plus one extreme 1,000,000ms
    # outlier -- large enough n that the 3*IQR fence actually catches it.
    normal_durations = [100.0, 120.0, 150.0, 180.0, 200.0, 220.0, 240.0, 260.0,
                        280.0, 300.0, 110.0, 130.0, 160.0, 190.0, 210.0, 230.0,
                        250.0, 270.0, 290.0, np.nan]
    durations = normal_durations + [1_000_000.0]
    n = len(durations)
    manufacturers = (["Apple", "Samsung"] * (n // 2)) + (["Apple"] if n % 2 else [])
    manufacturers[2] = None
    return pd.DataFrame({
        "Dur. (ms)": durations,
        "Handset Manufacturer": manufacturers[:n],
        "Social Media DL (Bytes)": [float(i) for i in range(n)],
        "Social Media UL (Bytes)": [float(i) / 10 for i in range(n)],
    })


def test_missing_numeric_filled_with_mean(sample_df):
    out = treat_missing_and_outliers(sample_df, cap_outliers=False)
    assert out["Dur. (ms)"].isna().sum() == 0
    expected_mean = sample_df["Dur. (ms)"].mean()
    missing_idx = sample_df["Dur. (ms)"].isna().idxmax()
    assert out.loc[missing_idx, "Dur. (ms)"] == pytest.approx(expected_mean)


def test_missing_categorical_filled_with_mode(sample_df):
    out = treat_missing_and_outliers(sample_df, cap_outliers=False)
    assert out["Handset Manufacturer"].isna().sum() == 0
    assert out.loc[2, "Handset Manufacturer"] in {"Apple", "Samsung"}


def test_outlier_capping_reduces_extreme_value(sample_df):
    out = treat_missing_and_outliers(sample_df, cap_outliers=True)
    assert out["Dur. (ms)"].max() < 1_000_000.0


def test_add_total_app_bytes_sums_dl_ul(sample_df):
    out = add_total_app_bytes(sample_df)
    assert "Total Social Media (Bytes)" in out.columns
    expected = sample_df["Social Media DL (Bytes)"] + sample_df["Social Media UL (Bytes)"]
    assert out["Total Social Media (Bytes)"].tolist() == expected.tolist()


def test_no_missing_left_after_treatment(sample_df):
    out = treat_missing_and_outliers(sample_df)
    assert out.isna().sum().sum() == 0
