# TellCo Telecom User Analytics

Due-diligence analysis of TellCo's xDR (session-level) network data, prepared
for an investor evaluating a potential acquisition. Covers four analysis
tasks -- User Overview, User Engagement, User Experience, and Customer
Satisfaction -- plus a Streamlit dashboard, a written investor report, and a
20-slide recommendation deck.

## Project layout

```
tellco-analysis/
├── data/               # Raw export + cleaned/derived feature tables (gitignored except samples)
├── src/tellco/         # Installable package: data_prep, feature_store, modeling
├── scripts/            # One script per task, run in order (see below)
├── tests/              # pytest unit tests for src/tellco
├── dashboard/app.py    # Streamlit dashboard
├── figures/            # Generated charts (PNG)
├── reports/            # Investor report, slide deck, model-tracking log
├── Dockerfile
├── requirements.txt / pyproject.toml
└── .github/workflows/ci.yml
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

## Running the analysis pipeline

```bash
python scripts/convert_to_csv.py        # one-time: xlsx -> csv (only needed if re-deriving from raw xlsx)
python scripts/task1_overview.py && python scripts/task1_plots.py
python scripts/task2_engagement.py && python scripts/task2_elbow.py && python scripts/task2_plots.py
python scripts/task3_experience.py && python scripts/task3_plots.py
python scripts/task4_satisfaction.py && python scripts/task4_db_export.py && python scripts/task4_model_tracking.py && python scripts/task4_plots.py
```

## Dashboard

```bash
streamlit run dashboard/app.py
```

## Tests

```bash
pytest tests/ --cov=src/tellco
```

## Docker

```bash
docker build -t tellco-analysis .
docker run -p 8501:8501 tellco-analysis
```

## Environment note: no scikit-learn / scipy / MySQL

This project was built in a sandbox with no outbound network access, so
`scikit-learn`, `scipy`, and a local MySQL server were not installable.
`src/tellco/modeling.py` ships small, dependency-free numpy implementations
of `StandardScaler`, `PCA`, `KMeans`, and `LinearRegression` with the same
`fit`/`transform`/`predict` API shape as scikit-learn, so the analysis runs
end-to-end anywhere. In a normal environment you can swap in the real
scikit-learn classes with no other code changes -- they're listed in
`requirements.txt` for that purpose. Similarly, Task 4.6's "export to local
MySQL" was done with SQLite (`data/tellco_satisfaction.db`,
`scripts/task4_db_export.py`) as a same-SQL-dialect stand-in; point
`to_sql()` at a SQLAlchemy MySQL engine to use real MySQL.

## Model tracking (Task 4.7 - MLOps)

`scripts/task4_model_tracking.py` logs each training run (code version,
start/end time, params, train/test R²/RMSE, and a coefficients artifact) to
`reports/model_tracking_log.csv` and `reports/model_runs/`, functioning as a
lightweight stand-in for MLflow/W&B in this offline sandbox.

## Key data-quality note

One MSISDN in the dataset has 1,000+ xDR sessions vs. a median of ~1 for all
other users -- an extreme outlier (likely an M2M SIM, aggregator line, or
data artifact) that dominates the engagement- and satisfaction-cluster
analysis. It is called out explicitly in the investor report as a limitation;
a production pipeline should segment or cap this class of user before
re-running the clustering.
