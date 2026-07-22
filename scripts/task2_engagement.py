import sys, json
sys.path.insert(0, "src")
import numpy as np
import pandas as pd
from tellco.data_prep import APP_COLUMNS
from tellco.feature_store import get_user_engagement_features
from tellco.modeling import StandardScaler, KMeans, elbow_method

pd.set_option("display.width", 200)
import time as _time
_t0=_time.time()
def _log(m):
    print(m, _time.time()-_t0, flush=True)
df = pd.read_pickle("data/clean_df.pkl")
_log("loaded df")
results = {}

# --- Aggregate engagement metrics per user ---
eng = get_user_engagement_features(df)
eng.to_csv("data/user_engagement_features.csv", index=False)
_log("eng features saved")

# --- Top 10 customers per engagement metric ---
top10 = {
    "sessions_frequency": eng.nlargest(10, "sessions_frequency")[["MSISDN/Number", "sessions_frequency"]].to_dict("records"),
    "total_duration_ms": eng.nlargest(10, "total_duration_ms")[["MSISDN/Number", "total_duration_ms"]].to_dict("records"),
    "total_traffic_bytes": eng.nlargest(10, "total_traffic_bytes")[["MSISDN/Number", "total_traffic_bytes"]].to_dict("records"),
}
results["top10_per_metric"] = top10

# --- Normalize + KMeans (k=3) ---
metric_cols = ["sessions_frequency", "total_duration_ms", "total_traffic_bytes"]
X = eng[metric_cols].values
scaler = StandardScaler().fit(X)
Xs = scaler.transform(X)
_log("starting kmeans3")
km3 = KMeans(n_clusters=3, n_init=10, random_state=42).fit(Xs)
_log("kmeans3 done")
eng["engagement_cluster"] = km3.labels_
eng.to_csv("data/user_engagement_features.csv", index=False)

# non-normalized cluster stats
cluster_stats = eng.groupby("engagement_cluster")[metric_cols].agg(["min", "max", "mean", "sum"])
results["engagement_cluster_stats"] = cluster_stats.round(2).to_string()

# identify least-engaged cluster (lowest mean total_traffic_bytes) -- needed later for Task 4
cluster_means = eng.groupby("engagement_cluster")[metric_cols].mean()
least_engaged_cluster = int(cluster_means["total_traffic_bytes"].idxmin())
results["least_engaged_cluster"] = least_engaged_cluster
results["cluster_centers_normalized"] = km3.cluster_centers_.tolist()
np.save("data/engagement_scaler_mean.npy", scaler.mean_)
np.save("data/engagement_scaler_scale.npy", scaler.scale_)
np.save("data/engagement_cluster_centers.npy", km3.cluster_centers_)
with open("data/engagement_meta.json", "w") as f:
    json.dump({"least_engaged_cluster": least_engaged_cluster, "metric_cols": metric_cols}, f)

# --- Per-application top 10 most engaged users ---
app_cols = [f"Total {app} (Bytes)" for app in APP_COLUMNS]
_log("starting per-app groupby")
per_app_totals = df.groupby("MSISDN/Number")[app_cols].sum().reset_index()
_log("per-app groupby done")
top10_per_app = {}
for col in app_cols:
    top10_per_app[col] = per_app_totals.nlargest(10, col)[["MSISDN/Number", col]].to_dict("records")
results["top10_per_app"] = top10_per_app

# --- Top 3 most used applications overall ---
app_totals = per_app_totals[app_cols].sum().sort_values(ascending=False)
results["app_totals_overall"] = app_totals.to_dict()
top3_apps = app_totals.head(3)
results["top3_apps"] = top3_apps.to_dict()

with open("data/task2_results_part1.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
np.save("data/engagement_Xs.npy", Xs)

print("TOP10 sessions_frequency"); print(pd.DataFrame(top10["sessions_frequency"]))
print("\nCLUSTER STATS\n", cluster_stats)
print("\nLEAST ENGAGED CLUSTER:", least_engaged_cluster)
print("\nAPP TOTALS OVERALL\n", app_totals)
print("PART1 DONE")
