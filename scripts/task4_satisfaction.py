import sys, json, time as _time
sys.path.insert(0, "src")
import numpy as np
import pandas as pd
from tellco.modeling import StandardScaler, KMeans, LinearRegression, euclidean_distance

pd.set_option("display.width", 200)
_t0 = _time.time()
def _log(m):
    print(m, _time.time() - _t0, flush=True)

eng = pd.read_csv("data/user_engagement_features.csv")
exp = pd.read_csv("data/user_experience_features.csv")
eng_meta = json.load(open("data/engagement_meta.json"))
exp_meta = json.load(open("data/experience_meta.json"))
eng_scaler_mean = np.load("data/engagement_scaler_mean.npy")
eng_scaler_scale = np.load("data/engagement_scaler_scale.npy")
eng_centers = np.load("data/engagement_cluster_centers.npy")
exp_scaler_mean = np.load("data/experience_scaler_mean.npy")
exp_scaler_scale = np.load("data/experience_scaler_scale.npy")
exp_centers = np.load("data/experience_cluster_centers.npy")

eng_metric_cols = eng_meta["metric_cols"]
exp_metric_cols = exp_meta["metric_cols"]
least_engaged = eng_meta["least_engaged_cluster"]
worst_exp = exp_meta["worst_experience_cluster"]

merged = eng.merge(exp, on="MSISDN/Number", how="inner", suffixes=("_eng", "_exp"))
_log(f"merged users: {merged.shape}")

# --- Task 4.1a: engagement score = distance to LEAST engaged cluster centroid ---
Xe = merged[eng_metric_cols].values
Xe_s = (Xe - eng_scaler_mean) / eng_scaler_scale
merged["engagement_score"] = euclidean_distance(Xe_s, eng_centers[least_engaged])

# --- Task 4.1b: experience score = distance to WORST experience cluster centroid ---
Xx = merged[exp_metric_cols].values
Xx_s = (Xx - exp_scaler_mean) / exp_scaler_scale
merged["experience_score"] = euclidean_distance(Xx_s, exp_centers[worst_exp])

# --- Task 4.2: satisfaction score = avg(engagement, experience) ---
merged["satisfaction_score"] = (merged["engagement_score"] + merged["experience_score"]) / 2
top10_satisfied = merged.nlargest(10, "satisfaction_score")[
    ["MSISDN/Number", "engagement_score", "experience_score", "satisfaction_score"]
]

results = {"top10_satisfied": top10_satisfied.to_dict("records")}

# --- Task 4.3: regression model to predict satisfaction score ---
feature_cols = eng_metric_cols + exp_metric_cols
Xr = merged[feature_cols].fillna(0).values
yr = merged["satisfaction_score"].values
scaler_r = StandardScaler().fit(Xr)
Xr_s = scaler_r.transform(Xr)
lr = LinearRegression().fit(Xr_s, yr)
r2 = lr.score(Xr_s, yr)
results["regression_r2"] = float(r2)
results["regression_coefficients"] = dict(zip(feature_cols, lr.coef_.tolist()))
results["regression_intercept"] = float(lr.intercept_)
_log("regression done")

# --- Task 4.4: KMeans (k=2) on engagement & experience scores ---
Xs2 = merged[["engagement_score", "experience_score"]].values
scaler2 = StandardScaler().fit(Xs2)
Xs2_n = scaler2.transform(Xs2)
km2 = KMeans(n_clusters=2, n_init=10, random_state=42).fit(Xs2_n)
merged["satisfaction_cluster"] = km2.labels_
_log("kmeans2 done")

# --- Task 4.5: aggregate avg satisfaction & experience score per cluster ---
cluster_agg = merged.groupby("satisfaction_cluster")[["satisfaction_score", "experience_score", "engagement_score"]].mean()
results["cluster_satisfaction_experience_avg"] = cluster_agg.round(4).to_dict(orient="index")

merged.to_csv("data/user_satisfaction_scores.csv", index=False)

with open("data/task4_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("TOP 10 SATISFIED CUSTOMERS")
print(top10_satisfied)
print("\nREGRESSION R2:", r2)
print("Coefficients:", dict(zip(feature_cols, lr.coef_.round(4).tolist())))
print("\nCLUSTER AGG\n", cluster_agg)
print("DONE")
