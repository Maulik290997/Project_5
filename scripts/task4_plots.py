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
m = pd.read_csv("data/user_satisfaction_scores.csv")

# 1. Engagement vs experience score, colored by satisfaction cluster (log scale due to outlier)
plt.figure(figsize=(8, 6))
sns.scatterplot(data=m, x="engagement_score", y="experience_score", hue="satisfaction_cluster",
                 palette="Set1", alpha=0.5, s=25)
plt.xscale("symlog")
plt.xlabel("Engagement score (distance to least-engaged cluster, log scale)")
plt.ylabel("Experience score (distance to worst-experience cluster)")
plt.title("Satisfaction Clusters (k=2) - Engagement vs Experience")
plt.tight_layout()
plt.savefig(f"{FIG}/satisfaction_clusters.png", dpi=150)
plt.close()

# 2. Distribution of satisfaction score, excluding the extreme outlier for readability
m_no_outlier = m[m["satisfaction_score"] < m["satisfaction_score"].quantile(0.999)]
plt.figure(figsize=(8, 5))
sns.histplot(m_no_outlier["satisfaction_score"], bins=60, kde=True, color="mediumpurple")
plt.xlabel("Satisfaction score")
plt.title("Distribution of Customer Satisfaction Scores (99.9th pct trimmed)")
plt.tight_layout()
plt.savefig(f"{FIG}/satisfaction_distribution.png", dpi=150)
plt.close()

# 3. Top 10 satisfied customers bar chart
top10 = m.nlargest(10, "satisfaction_score")
plt.figure(figsize=(9, 5))
sns.barplot(x=top10["satisfaction_score"], y=top10["MSISDN/Number"].astype(str), palette="flare", hue=top10["MSISDN/Number"].astype(str), legend=False)
plt.xlabel("Satisfaction score")
plt.ylabel("MSISDN")
plt.title("Top 10 Most Satisfied Customers")
plt.tight_layout()
plt.savefig(f"{FIG}/top10_satisfied.png", dpi=150)
plt.close()

# 4. Cluster averages
cluster_agg = m.groupby("satisfaction_cluster")[["satisfaction_score", "experience_score", "engagement_score"]].mean()
cluster_agg.to_csv("data/task4_cluster_avg.csv")
fig, ax = plt.subplots(figsize=(7, 5))
cluster_agg.plot(kind="bar", ax=ax, color=["mediumpurple", "steelblue", "salmon"])
plt.ylabel("Average score (log scale)")
plt.yscale("log")
plt.title("Average Satisfaction / Experience / Engagement by Cluster")
plt.tight_layout()
plt.savefig(f"{FIG}/satisfaction_cluster_avg.png", dpi=150)
plt.close()

print("TASK4 PLOTS SAVED")
