import sys
sys.path.insert(0, "src")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from tellco.data_prep import APP_COLUMNS
from tellco.modeling import StandardScaler, PCA

sns.set_theme(style="whitegrid")
df = pd.read_pickle("data/clean_df.pkl")
FIG = "figures"

# 1. Top 10 handsets bar chart
top_handsets = df["Handset Type"].value_counts().head(10)
plt.figure(figsize=(9, 5))
sns.barplot(x=top_handsets.values, y=top_handsets.index, palette="viridis")
plt.xlabel("Number of xDR sessions")
plt.title("Top 10 Handsets by Session Count")
plt.tight_layout()
plt.savefig(f"{FIG}/top10_handsets.png", dpi=150)
plt.close()

# 2. Top 3 manufacturers
top_manu = df["Handset Manufacturer"].value_counts().head(3)
plt.figure(figsize=(6, 5))
sns.barplot(x=top_manu.index, y=top_manu.values, palette="magma")
plt.ylabel("Number of xDR sessions")
plt.title("Top 3 Handset Manufacturers")
plt.tight_layout()
plt.savefig(f"{FIG}/top3_manufacturers.png", dpi=150)
plt.close()

# 3. Top 5 handsets per top-3 manufacturer (small multiples)
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for ax, manu in zip(axes, top_manu.index):
    sub = df[df["Handset Manufacturer"] == manu]["Handset Type"].value_counts().head(5)
    sns.barplot(x=sub.values, y=sub.index, ax=ax, palette="crest")
    ax.set_title(manu)
    ax.set_xlabel("Sessions")
plt.tight_layout()
plt.savefig(f"{FIG}/top5_handsets_per_manufacturer.png", dpi=150)
plt.close()

# 4. Univariate: histograms + boxplots for key quant vars
quant_vars = ["Dur. (ms)", "Total DL (Bytes)", "Total UL (Bytes)", "Avg RTT DL (ms)", "Avg Bearer TP DL (kbps)"]
fig, axes = plt.subplots(len(quant_vars), 2, figsize=(12, 4 * len(quant_vars)))
for i, col in enumerate(quant_vars):
    sns.histplot(df[col], bins=50, ax=axes[i, 0], kde=True, color="steelblue")
    axes[i, 0].set_title(f"Distribution: {col}")
    sns.boxplot(x=df[col], ax=axes[i, 1], color="salmon")
    axes[i, 1].set_title(f"Boxplot: {col}")
plt.tight_layout()
plt.savefig(f"{FIG}/univariate_analysis.png", dpi=150)
plt.close()

# 5. Bivariate: each app total bytes vs total data (scatter, sampled for speed)
app_cols = [f"Total {app} (Bytes)" for app in APP_COLUMNS]
df["total_data_bytes"] = df["Total DL (Bytes)"] + df["Total UL (Bytes)"]
sample = df.sample(min(5000, len(df)), random_state=42)
fig, axes = plt.subplots(3, 3, figsize=(14, 12))
axes = axes.flatten()
for i, col in enumerate(app_cols):
    axes[i].scatter(sample[col], sample["total_data_bytes"], alpha=0.2, s=8, color="teal")
    r = df[col].corr(df["total_data_bytes"])
    axes[i].set_title(f"{col.replace('Total ', '').replace(' (Bytes)', '')} vs Total (r={r:.3f})")
for j in range(len(app_cols), len(axes)):
    axes[j].axis("off")
plt.tight_layout()
plt.savefig(f"{FIG}/bivariate_app_vs_total.png", dpi=150)
plt.close()

# 6. Correlation heatmap
corr = df[app_cols].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            xticklabels=[c.replace("Total ", "").replace(" (Bytes)", "") for c in app_cols],
            yticklabels=[c.replace("Total ", "").replace(" (Bytes)", "") for c in app_cols])
plt.title("Correlation Matrix: Application Data Volumes")
plt.tight_layout()
plt.savefig(f"{FIG}/correlation_heatmap.png", dpi=150)
plt.close()

# 7. Decile segmentation
from tellco.feature_store import get_user_overview_features
uf = get_user_overview_features(df)
uf["duration_decile"] = pd.qcut(uf["total_duration_ms"].rank(method="first"), 10, labels=False) + 1
uf["total_data_bytes"] = uf["Total DL (Bytes)"] + uf["Total UL (Bytes)"]
decile_totals = uf.groupby("duration_decile")["total_data_bytes"].sum()
plt.figure(figsize=(9, 5))
sns.barplot(x=decile_totals.index, y=decile_totals.values, palette="flare")
plt.xlabel("Session-duration decile (1=shortest, 10=longest)")
plt.ylabel("Total data volume (Bytes)")
plt.title("Total Data Volume by Duration Decile Class")
plt.tight_layout()
plt.savefig(f"{FIG}/decile_segmentation.png", dpi=150)
plt.close()

# 8. PCA scree plot
X = df[app_cols].fillna(0).values
Xs = StandardScaler().fit_transform(X)
pca = PCA(n_components=7).fit(Xs)
plt.figure(figsize=(7, 5))
plt.bar(range(1, 8), pca.explained_variance_ratio_ * 100, color="darkorange")
plt.plot(range(1, 8), np.cumsum(pca.explained_variance_ratio_) * 100, color="black", marker="o")
plt.xlabel("Principal Component")
plt.ylabel("Explained variance (%)")
plt.title("PCA Scree Plot - Application Usage Dimensions")
plt.tight_layout()
plt.savefig(f"{FIG}/pca_scree.png", dpi=150)
plt.close()

print("ALL PLOTS SAVED")
