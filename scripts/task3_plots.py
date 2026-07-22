import sys, json
sys.path.insert(0, "src")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

sns.set_theme(style="whitegrid")
FIG = "figures"
exp = pd.read_csv("data/user_experience_features.csv")
results = json.load(open("data/task3_results.json"))

# 1. Distribution of avg throughput per handset type (top 15 handsets by volume)
top_handsets = exp["handset_type"].value_counts().head(15).index
sub = exp[exp["handset_type"].isin(top_handsets)]
plt.figure(figsize=(10, 8))
order = sub.groupby("handset_type")["avg_throughput_kbps"].median().sort_values(ascending=False).index
sns.boxplot(data=sub, y="handset_type", x="avg_throughput_kbps", order=order, palette="viridis", hue="handset_type", legend=False)
plt.xlabel("Average throughput (kbps)")
plt.title("Avg Throughput Distribution by Handset Type (Top 15 by volume)")
plt.tight_layout()
plt.savefig(f"{FIG}/throughput_by_handset.png", dpi=150)
plt.close()

# 2. Avg TCP retransmission per handset type (top 15 by volume)
plt.figure(figsize=(10, 8))
order2 = sub.groupby("handset_type")["avg_tcp_retrans_total_bytes"].mean().sort_values(ascending=False).index
sns.barplot(data=sub, y="handset_type", x="avg_tcp_retrans_total_bytes", order=order2, palette="rocket", hue="handset_type", legend=False, errorbar=None)
plt.xlabel("Average TCP retransmission (Bytes)")
plt.title("Avg TCP Retransmission by Handset Type (Top 15 by volume)")
plt.tight_layout()
plt.savefig(f"{FIG}/tcp_retrans_by_handset.png", dpi=150)
plt.close()

# 3. Experience clusters scatter (RTT vs Throughput, colored by cluster)
plt.figure(figsize=(8, 6))
sample = exp.sample(min(8000, len(exp)), random_state=42)
sns.scatterplot(data=sample, x="avg_rtt_ms", y="avg_throughput_kbps", hue="experience_cluster", palette="Set1", alpha=0.4, s=20)
plt.xlabel("Average RTT (ms)")
plt.ylabel("Average throughput (kbps)")
plt.title("User Experience Clusters (k=3)")
plt.tight_layout()
plt.savefig(f"{FIG}/experience_clusters_scatter.png", dpi=150)
plt.close()

# 4. Cluster averages bar chart
metric_cols = ["avg_tcp_retrans_total_bytes", "avg_rtt_ms", "avg_throughput_kbps"]
cluster_avg = exp.groupby("experience_cluster")[metric_cols].mean()
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, col in zip(axes, metric_cols):
    sns.barplot(x=cluster_avg.index, y=cluster_avg[col], ax=ax, hue=cluster_avg.index, palette="crest", legend=False)
    ax.set_title(f"Avg {col} per cluster")
plt.tight_layout()
plt.savefig(f"{FIG}/experience_cluster_averages.png", dpi=150)
plt.close()

print("TASK3 PLOTS SAVED")
