"""
Lightweight MLOps model-tracking log (stand-in for MLflow/Weights&Biases,
neither of which is installable in this offline sandbox). Appends one row
per training run with code version, timing, params, and metrics, and writes
a companion JSON artifact per run -- the same information MLflow would
capture, just persisted as CSV+JSON so it needs no server.
"""
import csv
import json
import os
import subprocess
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import sys
sys.path.insert(0, "src")
from tellco.modeling import StandardScaler, LinearRegression

LOG_CSV = "reports/model_tracking_log.csv"
ARTIFACT_DIR = "reports/model_runs"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

try:
    code_version = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
except Exception:
    code_version = "no-git-repo:v0.1.0"

run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
start_time = datetime.now(timezone.utc).isoformat()
t0 = time.time()

merged = pd.read_csv("data/user_satisfaction_scores.csv")
eng_meta = json.load(open("data/engagement_meta.json"))
exp_meta = json.load(open("data/experience_meta.json"))
feature_cols = eng_meta["metric_cols"] + exp_meta["metric_cols"]

X = merged[feature_cols].fillna(0).values
y = merged["satisfaction_score"].values
scaler = StandardScaler().fit(X)
Xs = scaler.transform(X)

# simple 80/20 holdout split (no sklearn train_test_split available)
rng = np.random.default_rng(42)
idx = rng.permutation(len(Xs))
split = int(0.8 * len(idx))
train_idx, test_idx = idx[:split], idx[split:]

model = LinearRegression().fit(Xs[train_idx], y[train_idx])
train_r2 = model.score(Xs[train_idx], y[train_idx])
test_r2 = model.score(Xs[test_idx], y[test_idx])
train_rmse = float(np.sqrt(np.mean((y[train_idx] - model.predict(Xs[train_idx])) ** 2)))
test_rmse = float(np.sqrt(np.mean((y[test_idx] - model.predict(Xs[test_idx])) ** 2)))

end_time = datetime.now(timezone.utc).isoformat()
duration_s = round(time.time() - t0, 3)

run_record = {
    "run_id": run_id,
    "code_version": code_version,
    "source": "scripts/task4_model_tracking.py",
    "model": "LinearRegression (numpy OLS, sklearn-API compatible)",
    "start_time": start_time,
    "end_time": end_time,
    "duration_s": duration_s,
    "n_train": int(len(train_idx)),
    "n_test": int(len(test_idx)),
    "features": feature_cols,
    "params": {"fit_intercept": True, "solver": "lstsq"},
    "metrics": {
        "train_r2": round(train_r2, 6),
        "test_r2": round(test_r2, 6),
        "train_rmse": round(train_rmse, 6),
        "test_rmse": round(test_rmse, 6),
    },
    "artifacts": {
        "coefficients_path": f"{ARTIFACT_DIR}/{run_id}_coefficients.json",
    },
}

with open(f"{ARTIFACT_DIR}/{run_id}_coefficients.json", "w") as f:
    json.dump(dict(zip(feature_cols, model.coef_.tolist())) | {"intercept": float(model.intercept_)}, f, indent=2)

write_header = not os.path.exists(LOG_CSV)
with open(LOG_CSV, "a", newline="") as f:
    writer = csv.writer(f)
    if write_header:
        writer.writerow([
            "run_id", "code_version", "source", "model", "start_time", "end_time",
            "duration_s", "n_train", "n_test", "train_r2", "test_r2", "train_rmse", "test_rmse"
        ])
    writer.writerow([
        run_record["run_id"], run_record["code_version"], run_record["source"], run_record["model"],
        run_record["start_time"], run_record["end_time"], run_record["duration_s"],
        run_record["n_train"], run_record["n_test"],
        run_record["metrics"]["train_r2"], run_record["metrics"]["test_r2"],
        run_record["metrics"]["train_rmse"], run_record["metrics"]["test_rmse"],
    ])

with open(f"{ARTIFACT_DIR}/{run_id}_full_record.json", "w") as f:
    json.dump(run_record, f, indent=2)

print(json.dumps(run_record, indent=2))
print("MODEL TRACKING LOGGED")
