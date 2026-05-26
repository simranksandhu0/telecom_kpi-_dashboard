"""
transform.py
Computes monthly KPIs across three domains:
  - Churn risk (churn rate, at-risk count, MoM trend)
  - Revenue (total, by plan, MoM variance)
  - Network (uptime, incidents, MTTR by region)
"""

import pandas as pd
import numpy as np


def compute_churn_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Monthly churn KPIs:
      - churn_rate        : churned / total customers
      - at_risk_count     : customers churned
      - mom_churn_change  : month-over-month change in churn rate
    """
    monthly = (
        df.groupby("date")
        .agg(
            total_customers=("customer_id", "count"),
            churned_count=("churned", "sum"),
        )
        .reset_index()
        .sort_values("date")
    )
    monthly["churn_rate"] = (
        monthly["churned_count"] / monthly["total_customers"]
    ).round(4)
    monthly["mom_churn_change"] = monthly["churn_rate"].diff().round(4)
    monthly.rename(columns={"churned_count": "at_risk_count"}, inplace=True)
    return monthly


def compute_revenue_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Monthly revenue KPIs:
      - total_revenue     : sum of revenue
      - revenue_by_plan   : pivot of revenue per plan type
      - mom_revenue_pct   : month-over-month % change in total revenue
    """
    monthly_total = (
        df.groupby("date")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"revenue": "total_revenue"})
        .sort_values("date")
    )
    monthly_total["mom_revenue_pct"] = (
        monthly_total["total_revenue"].pct_change().round(4)
    )

    by_plan = (
        df.groupby(["date", "plan"])["revenue"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    by_plan.columns.name = None

    merged = monthly_total.merge(by_plan, on="date", how="left")
    return merged


def compute_network_kpis(df_network: pd.DataFrame) -> pd.DataFrame:
    """
    Monthly network KPIs aggregated from daily regional data:
      - avg_uptime_pct    : mean uptime across regions
      - total_incidents   : sum of incidents
      - avg_mttr_hours    : average MTTR (excluding zero-incident days)
    """
    # Add month column for grouping
    df = df_network.copy()
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        df.groupby("month")
        .agg(
            avg_uptime_pct=("uptime_pct", "mean"),
            total_incidents=("incidents", "sum"),
        )
        .reset_index()
        .rename(columns={"month": "date"})
    )

    # MTTR average — only where incidents occurred (mttr=0 means no incident)
    df_with_incidents = df[df["mttr_hours"] > 0]
    avg_mttr = (
        df_with_incidents.groupby(df_with_incidents["date"].dt.to_period("M").dt.to_timestamp())
        ["mttr_hours"]
        .mean()
        .reset_index()
        .rename(columns={"date": "date", "mttr_hours": "avg_mttr_hours"})
    )

    monthly = monthly.merge(avg_mttr, on="date", how="left")
    monthly["avg_uptime_pct"] = monthly["avg_uptime_pct"].round(3)
    monthly["avg_mttr_hours"] = monthly["avg_mttr_hours"].round(2)
    return monthly
