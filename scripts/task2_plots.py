import sys, json
sys.path.insert(0, "src")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from tellco.data_prep import APP_COLUMNS

sns.set_theme(style="whitegrid")
FIG = "figures"
eng = pd.read_csv("data/user_engagement_features.csv")
elbow = json.load(open("data/task2_elbow.json"))

# 1. Elbow plot
ks, inertias = zip(*elbow)
plt.figure(figsize=(7, 5))
plt.plot(ks, inertias, marker="o", color="firebrick")
plt.xlabel("k (number of clusters)")
plt.ylabel("Inertia (within-cluster SSE)")
plt.title("Elbow Method for Optimal k - User Engagement")
plt.tight_layout()
plt.savefig(f"{FIG}/engagement_elbow.png", dpi=150)
plt.close()

# 2. Cluster scatter (duration vs traffic, colored by cluster)
plt.figure(figsize=(8, 6))
sns.scatterplot(
    data=eng, x="total_duration_ms", y="total_traffic_bytes",
    hue="engagement_cluster", palette="Set2", alpha=0.4, s=20
)
plt.xlabel("Total session duration (ms)")
plt.ylabel("Total traffic (Bytes)")
plt.title("User Engagement Clusters (k=3)")
plt.tight_layout()
plt.savefig(f"{FIG}/engagement_clusters_scatter.png", dpi=150)
plt.close()

# 3. Cluster metric averages (bar chart, non-normalized)
cluster_avg = eng.groupby("engagement_cluster")[
    ["sessions_frequency", "total_duration_ms", "total_traffic_bytes"]
].mean()
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, col in zip(axes, cluster_avg.columns):
    sns.barplot(x=cluster_avg.index, y=cluster_avg[col], ax=ax, hue=cluster_avg.index, palette="crest", legend=False)
    ax.set_title(f"Avg {col} per cluster")
plt.tight_layout()
plt.savefig(f"{FIG}/engagement_cluster_averages.png", dpi=150)
plt.close()

# 4. Top 3 most used applications
app_totals = json.load(open("data/task2_results.json"))["app_totals_overall"]
app_totals = pd.Series(app_totals).sort_values(ascending=False)
top3 = app_totals.head(3)
plt.figure(figsize=(7, 5))
sns.barplot(x=[c.replace("Total ", "").replace(" (Bytes)", "") for c in top3.index],
            y=top3.values, hue=[c for c in top3.index], palette="rocket", legend=False)
plt.ylabel("Total network traffic (Bytes)")
plt.title("Top 3 Most-Used Applications (Network-wide)")
plt.tight_layout()
plt.savefig(f"{FIG}/top3_applications.png", dpi=150)
plt.close()

print("TASK2 PLOTS SAVED")
