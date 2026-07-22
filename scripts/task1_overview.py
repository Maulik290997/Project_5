import sys, json
sys.path.insert(0, "src")
import numpy as np
import pandas as pd
from tellco.feature_store import get_user_overview_features
from tellco.modeling import StandardScaler, PCA

pd.set_option("display.width", 200)
df = pd.read_pickle("data/clean_df.pkl")

results = {}

# --- Top 10 handsets ---
top_handsets = df["Handset Type"].value_counts().head(10)
results["top_10_handsets"] = top_handsets.to_dict()

# --- Top 3 manufacturers ---
top_manufacturers = df["Handset Manufacturer"].value_counts().head(3)
results["top_3_manufacturers"] = top_manufacturers.to_dict()

# --- Top 5 handsets per top 3 manufacturers ---
top5_per_manu = {}
for manu in top_manufacturers.index:
    sub = df[df["Handset Manufacturer"] == manu]["Handset Type"].value_counts().head(5)
    top5_per_manu[manu] = sub.to_dict()
results["top5_handsets_per_manufacturer"] = top5_per_manu

# --- Task 1.1: per-user aggregation ---
user_features = get_user_overview_features(df)
user_features.to_csv("data/user_overview_features.csv", index=False)
results["n_users"] = int(user_features.shape[0])

# --- Basic metrics on key quantitative vars ---
quant_vars = [
    "Dur. (ms)", "Total DL (Bytes)", "Total UL (Bytes)",
    "Avg RTT DL (ms)", "Avg RTT UL (ms)",
    "Avg Bearer TP DL (kbps)", "Avg Bearer TP UL (kbps)",
]
basic_metrics = df[quant_vars].agg(["mean", "median", "std", "min", "max"]).T
results["basic_metrics"] = basic_metrics.round(2).to_dict(orient="index")

# --- Non-graphical univariate dispersion ---
dispersion_vars = [
    "Dur. (ms)", "Total DL (Bytes)", "Total UL (Bytes)",
    "Social Media_total_bytes" if "Social Media_total_bytes" in df.columns else "Social Media DL (Bytes)",
]
disp = df[quant_vars].agg(["std", "var", lambda s: s.quantile(0.75) - s.quantile(0.25), "skew", "kurt"]).T
disp.columns = ["std", "var", "iqr", "skew", "kurt"]
results["dispersion"] = disp.round(2).to_dict(orient="index")

# --- Bivariate: each app total bytes vs total DL+UL ---
from tellco.data_prep import APP_COLUMNS
app_cols = [f"Total {app} (Bytes)" for app in APP_COLUMNS]
df["total_data_bytes"] = df["Total DL (Bytes)"] + df["Total UL (Bytes)"]
bivariate_corr = {c: float(df[c].corr(df["total_data_bytes"])) for c in app_cols}
results["bivariate_corr_with_total"] = bivariate_corr

# --- Decile segmentation by total duration ---
user_features["duration_decile"] = pd.qcut(
    user_features["total_duration_ms"].rank(method="first"), 10, labels=False
)
user_features["total_data_bytes"] = (
    user_features["Total DL (Bytes)"] + user_features["Total UL (Bytes)"]
)
top5_deciles = user_features[user_features["duration_decile"] >= 5]
decile_summary = top5_deciles.groupby("duration_decile")["total_data_bytes"].sum()
results["top5_decile_total_data"] = {int(k): float(v) for k, v in decile_summary.to_dict().items()}

# --- Correlation matrix ---
corr_cols = app_cols
corr_matrix = df[corr_cols].corr()
corr_matrix.to_csv("data/task1_correlation_matrix.csv")
results["correlation_matrix"] = corr_matrix.round(3).to_dict()

# --- PCA ---
X = df[corr_cols].fillna(0).values
Xs = StandardScaler().fit_transform(X)
pca = PCA(n_components=4).fit(Xs)
results["pca_explained_variance_ratio"] = pca.explained_variance_ratio_.tolist()
results["pca_components"] = pca.components_.tolist()

with open("data/task1_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("TOP 10 HANDSETS")
print(top_handsets)
print()
print("TOP 3 MANUFACTURERS")
print(top_manufacturers)
print()
print("TOP 5 PER MANUFACTURER")
for k, v in top5_per_manu.items():
    print(k, v)
print()
print("BASIC METRICS")
print(basic_metrics)
print()
print("DISPERSION")
print(disp)
print()
print("BIVARIATE CORR (app total bytes vs total DL+UL)")
print(bivariate_corr)
print()
print("TOP 5 DECILES TOTAL DATA")
print(decile_summary)
print()
print("CORR MATRIX")
print(corr_matrix.round(2))
print()
print("PCA explained variance ratio", pca.explained_variance_ratio_)
print("DONE")
