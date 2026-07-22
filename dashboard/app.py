"""
TellCo Telecom Analytics Dashboard
-----------------------------------
Streamlit app surfacing the User Overview, Engagement, Experience, and
Satisfaction findings for the investor due-diligence project.

Run with:  streamlit run dashboard/app.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tellco.data_prep import APP_COLUMNS

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

st.set_page_config(page_title="TellCo Telecom Analytics", layout="wide", page_icon="\U0001F4F6")
sns.set_theme(style="whitegrid")


@st.cache_data
def load_clean_df():
    return pd.read_pickle(os.path.join(DATA_DIR, "clean_df.pkl"))


@st.cache_data
def load_csv(name):
    return pd.read_csv(os.path.join(DATA_DIR, name))


@st.cache_data
def load_json(name):
    with open(os.path.join(DATA_DIR, name)) as f:
        return json.load(f)


def page_overview():
    st.header("User Overview Analysis")
    df = load_clean_df()

    top_n = st.slider("Top N handsets to display", min_value=5, max_value=20, value=10)
    top_handsets = df["Handset Type"].value_counts().head(top_n)

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(8, max(4, top_n * 0.35)))
        sns.barplot(x=top_handsets.values, y=top_handsets.index, ax=ax, hue=top_handsets.index,
                    palette="viridis", legend=False)
        ax.set_xlabel("xDR sessions")
        ax.set_title(f"Top {top_n} Handsets")
        st.pyplot(fig)
    with col2:
        st.metric("Total users (MSISDN)", f"{df['MSISDN/Number'].nunique():,}")
        st.metric("Total xDR sessions", f"{len(df):,}")
        top_manu = df["Handset Manufacturer"].value_counts().head(3)
        st.subheader("Top 3 Manufacturers")
        st.dataframe(top_manu.rename("sessions"))

    st.subheader("Top 5 Handsets per Top-3 Manufacturer")
    manu_choice = st.selectbox("Manufacturer", top_manu.index)
    sub = df[df["Handset Manufacturer"] == manu_choice]["Handset Type"].value_counts().head(5)
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    sns.barplot(x=sub.values, y=sub.index, ax=ax2, hue=sub.index, palette="crest", legend=False)
    ax2.set_xlabel("Sessions")
    st.pyplot(fig2)

    st.subheader("Application Data Volume Correlation")
    app_cols = [f"Total {app} (Bytes)" for app in APP_COLUMNS]
    corr = df[app_cols].corr()
    fig3, ax3 = plt.subplots(figsize=(7, 5))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax3,
        xticklabels=[c.replace("Total ", "").replace(" (Bytes)", "") for c in app_cols],
        yticklabels=[c.replace("Total ", "").replace(" (Bytes)", "") for c in app_cols],
    )
    st.pyplot(fig3)


def page_engagement():
    st.header("User Engagement Analysis")
    eng = load_csv("user_engagement_features.csv")
    results = load_json("task2_results.json")

    metric = st.selectbox(
        "Engagement metric", ["sessions_frequency", "total_duration_ms", "total_traffic_bytes"]
    )
    top10 = eng.nlargest(10, metric)[["MSISDN/Number", metric]]
    st.subheader(f"Top 10 customers by {metric}")
    st.dataframe(top10, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Engagement Clusters (k=3)")
        fig, ax = plt.subplots(figsize=(6, 5))
        sample = eng.sample(min(8000, len(eng)), random_state=42)
        sns.scatterplot(
            data=sample, x="total_duration_ms", y="total_traffic_bytes",
            hue="engagement_cluster", palette="Set2", alpha=0.4, s=18, ax=ax
        )
        st.pyplot(fig)
    with col2:
        st.subheader("Elbow Method (optimal k)")
        elbow = results["elbow_inertias"]
        ks = [e[0] for e in elbow]
        inertias = [e[1] for e in elbow]
        fig2, ax2 = plt.subplots(figsize=(6, 5))
        ax2.plot(ks, inertias, marker="o", color="firebrick")
        ax2.set_xlabel("k")
        ax2.set_ylabel("Inertia")
        st.pyplot(fig2)

    st.subheader("Top 3 Most-Used Applications (network-wide)")
    app_totals = pd.Series(results["app_totals_overall"]).sort_values(ascending=False).head(3)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    sns.barplot(
        x=[c.replace("Total ", "").replace(" (Bytes)", "") for c in app_totals.index],
        y=app_totals.values, hue=app_totals.index, palette="rocket", legend=False, ax=ax3,
    )
    st.pyplot(fig3)


def page_experience():
    st.header("User Experience Analysis")
    exp = load_csv("user_experience_features.csv")

    metric = st.radio(
        "Metric", ["avg_throughput_kbps", "avg_tcp_retrans_total_bytes", "avg_rtt_ms"], horizontal=True
    )
    top_handsets = exp["handset_type"].value_counts().head(15).index
    sub = exp[exp["handset_type"].isin(top_handsets)]
    order = sub.groupby("handset_type")[metric].mean().sort_values(ascending=False).index

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.boxplot(data=sub, y="handset_type", x=metric, order=order, hue="handset_type",
                palette="viridis", legend=False, ax=ax)
    ax.set_title(f"{metric} by Handset Type (Top 15 by volume)")
    st.pyplot(fig)

    st.subheader("Experience Clusters (k=3)")
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    sample = exp.sample(min(8000, len(exp)), random_state=42)
    sns.scatterplot(data=sample, x="avg_rtt_ms", y="avg_throughput_kbps",
                     hue="experience_cluster", palette="Set1", alpha=0.4, s=18, ax=ax2)
    st.pyplot(fig2)


def page_satisfaction():
    st.header("Customer Satisfaction Analysis")
    sat = load_csv("user_satisfaction_scores.csv")

    top10 = sat.nlargest(10, "satisfaction_score")[
        ["MSISDN/Number", "engagement_score", "experience_score", "satisfaction_score"]
    ]
    st.subheader("Top 10 Most Satisfied Customers")
    st.dataframe(top10, use_container_width=True)
    st.caption(
        "Note: the single highest-scoring MSISDN is an extreme statistical outlier "
        "(1,000+ sessions vs. a median of ~1) -- likely an M2M/aggregator line rather "
        "than a typical retail customer. See report limitations."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Satisfaction Score Distribution")
        trimmed = sat[sat["satisfaction_score"] < sat["satisfaction_score"].quantile(0.999)]
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(trimmed["satisfaction_score"], bins=50, kde=True, color="mediumpurple", ax=ax)
        st.pyplot(fig)
    with col2:
        st.subheader("Avg Scores per Cluster (k=2)")
        cluster_avg = sat.groupby("satisfaction_cluster")[
            ["satisfaction_score", "experience_score", "engagement_score"]
        ].mean()
        st.dataframe(cluster_avg, use_container_width=True)

    st.subheader("Regression Model: Predicting Satisfaction Score")
    task4 = load_json("task4_results.json")
    st.write(f"R² (in-sample): **{task4['regression_r2']:.4f}**")
    coef = pd.Series(task4["regression_coefficients"]).sort_values()
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    sns.barplot(x=coef.values, y=coef.index, hue=coef.index, palette="crest", legend=False, ax=ax2)
    ax2.set_title("Standardized regression coefficients")
    st.pyplot(fig2)


def page_summary():
    st.header("Executive Summary & Recommendation")
    st.markdown(
        """
        This dashboard summarizes a full-funnel analysis of TellCo's xDR network
        data: user overview, engagement, network experience, and derived
        satisfaction scores. Use the sidebar to explore each task in detail.

        Key takeaways are documented in the accompanying investor report and
        slide deck, including the growth/purchase recommendation and analysis
        limitations.
        """
    )


PAGES = {
    "Executive Summary": page_summary,
    "1. User Overview": page_overview,
    "2. User Engagement": page_engagement,
    "3. User Experience": page_experience,
    "4. Satisfaction": page_satisfaction,
}

st.sidebar.title("TellCo Analytics")
choice = st.sidebar.radio("Navigate", list(PAGES.keys()))
PAGES[choice]()
