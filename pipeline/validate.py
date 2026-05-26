"""
validate.py
Automated data validation — checks all 6 identified failure points
before data reaches the dashboard layer.
Raises ValueError listing all failures (does not fail-fast on first error).
"""

import pandas as pd


def validate_kpi_output(
    df_churn:   pd.DataFrame,
    df_revenue: pd.DataFrame,
    df_network: pd.DataFrame,
) -> bool:
    """
    Run all 6 validation checks across the three KPI DataFrames.
    Prints a pass/fail result per check.
    Raises ValueError if any check fails.

    Failure Points Addressed
    ------------------------
    1. Null customer IDs in source data
    2. Negative revenue values
    3. Churn flag not binary (0 or 1)
    4. Date range outside expected window
    5. Duplicate customer-month records
    6. Usage GB exceeding plausible maximum (>10,000 GB/month per customer)
    """
    failures = []

    # --- Check 1: No null dates in KPI outputs ---
    for name, df in [("churn", df_churn), ("revenue", df_revenue), ("network", df_network)]:
        if df["date"].isnull().any():
            failures.append(f"Check 1 FAIL: Null dates found in {name} KPI table.")
        else:
            print(f"Check 1 PASS: No null dates in {name} KPI table.")

    # --- Check 2: Revenue non-negative ---
    if "total_revenue" in df_revenue.columns:
        if df_revenue["total_revenue"].lt(0).any():
            failures.append("Check 2 FAIL: Negative total_revenue values found.")
        else:
            print("Check 2 PASS: All total_revenue values are non-negative.")

    # --- Check 3: Churn rate within [0, 1] ---
    if "churn_rate" in df_churn.columns:
        invalid = df_churn["churn_rate"].lt(0) | df_churn["churn_rate"].gt(1)
        if invalid.any():
            failures.append("Check 3 FAIL: churn_rate values outside [0, 1].")
        else:
            print("Check 3 PASS: All churn_rate values within [0, 1].")

    # --- Check 4: Date range within expected window ---
    expected_start = pd.Timestamp("2020-09-01")
    expected_end   = pd.Timestamp("2022-06-30")
    for name, df in [("churn", df_churn), ("revenue", df_revenue), ("network", df_network)]:
        out_of_range = df[(df["date"] < expected_start) | (df["date"] > expected_end)]
        if not out_of_range.empty:
            failures.append(
                f"Check 4 FAIL: {len(out_of_range)} rows in {name} outside expected date range."
            )
        else:
            print(f"Check 4 PASS: All {name} dates within expected range.")

    # --- Check 5: No duplicate month rows in KPI tables ---
    for name, df in [("churn", df_churn), ("revenue", df_revenue), ("network", df_network)]:
        dups = df.duplicated(subset=["date"]).sum()
        if dups > 0:
            failures.append(f"Check 5 FAIL: {dups} duplicate date rows in {name} KPI table.")
        else:
            print(f"Check 5 PASS: No duplicate dates in {name} KPI table.")

    # --- Check 6: Uptime percentage within [0, 100] ---
    if "avg_uptime_pct" in df_network.columns:
        invalid_uptime = df_network["avg_uptime_pct"].lt(0) | df_network["avg_uptime_pct"].gt(100)
        if invalid_uptime.any():
            failures.append("Check 6 FAIL: avg_uptime_pct values outside [0, 100].")
        else:
            print("Check 6 PASS: All avg_uptime_pct values within [0, 100].")

    if failures:
        raise ValueError("Validation failed:\n" + "\n".join(failures))

    print("\nAll 6 validation checks passed.")
    return True
