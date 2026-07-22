import sys, json
sys.path.insert(0, "src")
import time as _time
import numpy as np
import pandas as pd
from tellco.feature_store import get_user_experience_features
from tellco.modeling import StandardScaler, KMeans

pd.set_option("display.width", 200)
_t0 = _time.time()
def _log(m):
    print(m, _time.time() - _t0, flush=True)

df = pd.read_pickle("data/clean_df.pkl")
_log("loaded df")
results = {}

# --- Task 3.1: per-customer aggregation ---
exp = get_user_experience_features(df)
exp.to_csv("data/user_experience_features.csv", index=False)
_log("experience features saved")

# --- Task 3.2: top/bottom/most-frequent 10 for TCP, RTT, throughput ---
def top_bottom_freq(series, name):
    s = series.dropna()
    return {
        f"{name}_top10": s.nlargest(10).tolist(),
        f"{name}_bottom10": s.nsmallest(10).tolist(),
        f"{name}_most_frequent10": s.value_counts().head(10).to_dict(),
    }

tcp_stats = top_bottom_freq(
    df["TCP DL Retrans. Vol (Bytes)"].fillna(0) + df["TCP UL Retrans. Vol (Bytes)"].fillna(0), "tcp"
)
rtt_stats = top_bottom_freq(
    df["Avg RTT DL (ms)"].fillna(0) + df["Avg RTT UL (ms)"].fillna(0), "rtt"
)
tp_stats = top_bottom_freq(
    df["Avg Bearer TP DL (kbps)"].fillna(0) + df["Avg Bearer TP UL (kbps)"].fillna(0), "throughput"
)
results.update(tcp_stats)
results.update(rtt_stats)
results.update(tp_stats)
_log("top/bottom/freq computed")

# --- Task 3.3: distribution of avg throughput & TCP retransmission per handset type ---
throughput_by_handset = exp.groupby("handset_type")["avg_throughput_kbps"].mean().sort_values(ascending=False)
tcp_by_handset = exp.groupby("handset_type")["avg_tcp_retrans_total_bytes"].mean().sort_values(ascending=False)
results["throughput_by_handset_top15"] = throughput_by_handset.head(15).to_dict()
results["throughput_by_handset_bottom15"] = throughput_by_handset.tail(15).to_dict()
results["tcp_by_handset_top15"] = tcp_by_handset.head(15).to_dict()
_log("handset distributions computed")

# --- Task 3.4: KMeans (k=3) experience clusters ---
metric_cols = ["avg_tcp_retrans_total_bytes", "avg_rtt_ms", "avg_throughput_kbps"]
exp_clean = exp.dropna(subset=metric_cols).copy()
X = exp_clean[metric_cols].values
scaler = StandardScaler().fit(X)
Xs = scaler.transform(X)
km3 = KMeans(n_clusters=3, n_init=10, random_state=42).fit(Xs)
exp_clean["experience_cluster"] = km3.labels_
exp_clean.to_csv("data/user_experience_features.csv", index=False)
_log("kmeans3 experience done")

cluster_stats = exp_clean.groupby("experience_cluster")[metric_cols].agg(["min", "max", "mean"])
results["experience_cluster_stats"] = cluster_stats.round(2).to_string()

# worst experience cluster = highest TCP retrans + highest RTT + lowest throughput
cluster_means = exp_clean.groupby("experience_cluster")[metric_cols].mean()
# simple composite "badness" score to pick worst cluster
badness = (
    cluster_means["avg_tcp_retrans_total_bytes"].rank()
    + cluster_means["avg_rtt_ms"].rank()
    - cluster_means["avg_throughput_kbps"].rank()
)
worst_experience_cluster = int(badness.idxmax())
results["worst_experience_cluster"] = worst_experience_cluster
results["experience_cluster_centers_normalized"] = km3.cluster_centers_.tolist()

np.save("data/experience_scaler_mean.npy", scaler.mean_)
np.save("data/experience_scaler_scale.npy", scaler.scale_)
np.save("data/experience_cluster_centers.npy", km3.cluster_centers_)
with open("data/experience_meta.json", "w") as f:
    json.dump({"worst_experience_cluster": worst_experience_cluster, "metric_cols": metric_cols}, f)

with open("data/task3_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("THROUGHPUT BY HANDSET (top10)\n", throughput_by_handset.head(10))
print("\nTCP BY HANDSET (top10)\n", tcp_by_handset.head(10))
print("\nCLUSTER STATS\n", cluster_stats)
print("\nWORST EXPERIENCE CLUSTER:", worst_experience_cluster)
print("DONE")
