"""
load.py
Writes validated KPI tables to the processed output layer (parquet).
"""

import pandas as pd
from pathlib import Path


OUTPUT_DIR = Path("data/processed")


def save_kpis(
    df_churn:   pd.DataFrame,
    df_revenue: pd.DataFrame,
    df_network: pd.DataFrame,
) -> None:
    """Save all three KPI tables to the processed data directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df_churn.to_parquet(OUTPUT_DIR / "kpi_churn.parquet",   index=False)
    df_revenue.to_parquet(OUTPUT_DIR / "kpi_revenue.parquet", index=False)
    df_network.to_parquet(OUTPUT_DIR / "kpi_network.parquet", index=False)

    print(f"Churn KPI  : {len(df_churn):,} rows → {OUTPUT_DIR / 'kpi_churn.parquet'}")
    print(f"Revenue KPI: {len(df_revenue):,} rows → {OUTPUT_DIR / 'kpi_revenue.parquet'}")
    print(f"Network KPI: {len(df_network):,} rows → {OUTPUT_DIR / 'kpi_network.parquet'}")
    print("Load complete.")
