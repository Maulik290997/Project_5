import sqlite3
import pandas as pd

m = pd.read_csv("data/user_satisfaction_scores.csv")
final_table = m[[
    "MSISDN/Number", "engagement_score", "experience_score",
    "satisfaction_score", "satisfaction_cluster"
]].rename(columns={"MSISDN/Number": "user_id"})

# NOTE: this sandbox has no local MySQL server available, so we export to
# SQLite (same relational semantics / SQL dialect close enough for the
# assignment's screenshot requirement) as a drop-in stand-in. To point this
# at a real MySQL instance, swap the sqlite3 connection below for
# `mysql.connector.connect(...)` or a SQLAlchemy engine with
# `mysql+pymysql://user:pass@host/db` and use `final_table.to_sql(...)`.
conn = sqlite3.connect("/tmp/tellco_satisfaction.db")
final_table.to_sql("user_satisfaction_scores", conn, if_exists="replace", index=False)

cur = conn.cursor()
cur.execute("""
    SELECT user_id, engagement_score, experience_score, satisfaction_score
    FROM user_satisfaction_scores
    ORDER BY satisfaction_score DESC
    LIMIT 10;
""")
rows = cur.fetchall()
print(f"{'user_id':>15} | {'engagement':>12} | {'experience':>12} | {'satisfaction':>12}")
print("-" * 60)
for r in rows:
    print(f"{r[0]:>15.0f} | {r[1]:>12.4f} | {r[2]:>12.4f} | {r[3]:>12.4f}")

cur.execute("SELECT COUNT(*) FROM user_satisfaction_scores;")
print("\nTotal rows exported:", cur.fetchone()[0])
conn.close()
