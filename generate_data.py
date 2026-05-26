"""
generate_data.py
Generates synthetic telecom KPI data:
  - customer-level data (churn, usage, revenue)
  - network incidents
Saves to data/telecom_customers.parquet and data/network_incidents.parquet
"""

import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
N_CUSTOMERS = 50_000
START_DATE  = pd.Timestamp("2020-09-01")
END_DATE    = pd.Timestamp("2022-06-30")


def generate_customer_data(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(START_DATE, END_DATE, freq="MS")
    n_months = len(dates)

    records = []
    for month_idx, month in enumerate(dates):
        n = N_CUSTOMERS
        customer_ids = [f"T{str(i).zfill(6)}" for i in range(1, n + 1)]

        usage_gb   = rng.exponential(scale=15, size=n).round(2)
        revenue    = (usage_gb * rng.uniform(2, 5, size=n) + rng.normal(20, 5, size=n)).clip(0).round(2)
        plan       = rng.choice(["Basic", "Standard", "Premium"], size=n, p=[0.4, 0.4, 0.2])

        # Churn risk: higher for low usage, older tenure simulation
        churn_score = (usage_gb < 5).astype(int) + (revenue < 25).astype(int) + rng.integers(0, 2, size=n)
        churned = (churn_score >= 2).astype(int)

        df_month = pd.DataFrame({
            "date":        month.strftime("%Y-%m-%d"),
            "customer_id": customer_ids,
            "plan":        plan,
            "usage_gb":    usage_gb,
            "revenue":     revenue,
            "churned":     churned,
        })
        records.append(df_month)

    df = pd.concat(records, ignore_index=True)
    return df


def generate_network_data(seed: int = SEED + 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    regions = ["North", "South", "East", "West", "Central"]

    records = []
    for date in dates:
        for region in regions:
            incidents  = rng.integers(0, 5)
            uptime_pct = round(float(rng.uniform(97.5, 100.0)), 3)
            # MTTR: mean time to resolve in hours
            mttr_hours = round(float(rng.uniform(0.5, 6.0)), 2) if incidents > 0 else 0.0

            records.append({
                "date":        date.strftime("%Y-%m-%d"),
                "region":      region,
                "incidents":   int(incidents),
                "uptime_pct":  uptime_pct,
                "mttr_hours":  mttr_hours,
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)

    print("Generating customer data...")
    df_customers = generate_customer_data()
    df_customers.to_parquet("data/telecom_customers.parquet", index=False)
    print(f"Saved {len(df_customers):,} customer-month rows to data/telecom_customers.parquet")

    print("Generating network data...")
    df_network = generate_network_data()
    df_network.to_parquet("data/network_incidents.parquet", index=False)
    print(f"Saved {len(df_network):,} network rows to data/network_incidents.parquet")
