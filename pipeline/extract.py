"""
extract.py
Loads raw telecom data from parquet files and runs schema validation.
"""

import pandas as pd
from pathlib import Path


CUSTOMER_REQUIRED = {"date", "customer_id", "plan", "usage_gb", "revenue", "churned"}
NETWORK_REQUIRED  = {"date", "region", "incidents", "uptime_pct", "mttr_hours"}


def load_customers(path: str = "data/telecom_customers.parquet") -> pd.DataFrame:
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} not found. Run generate_data.py first.")
    df = pd.read_parquet(path)
    missing = CUSTOMER_REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Customer data missing columns: {missing}")
    df["date"] = pd.to_datetime(df["date"])
    print(f"Loaded {len(df):,} customer-month rows.")
    return df


def load_network(path: str = "data/network_incidents.parquet") -> pd.DataFrame:
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} not found. Run generate_data.py first.")
    df = pd.read_parquet(path)
    missing = NETWORK_REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Network data missing columns: {missing}")
    df["date"] = pd.to_datetime(df["date"])
    print(f"Loaded {len(df):,} network rows.")
    return df
