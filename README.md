# Telecom KPI Dashboard

> A unified Power BI reporting suite consolidating churn risk, revenue trends, and network performance across a 2TB telecom dataset — adopted as the primary weekly decision tool by senior leadership within 3 months.

---

## Overview

Four cross-functional teams. A 2TB telecom dataset. No shared view of performance. Every team was working from their own slice of the data — no one could see the full picture, and leadership had no single source of truth for weekly decisions.

This project fixed that. A consolidated KPI framework and Power BI dashboard suite brought churn risk, revenue, and network performance into one place — presented to 15+ senior stakeholders, iterated through 3 feedback cycles, and formally adopted as the standard weekly reporting suite.

On top of that, the manual reporting pipeline that fed this data was re-engineered using Python and Apache Spark, cutting end-to-end cycle time by 40% and eliminating 15 hours of manual effort per week.

---

## Problem Statement

- Four cross-functional teams (network, revenue, customer success, and operations) each had siloed views of performance — no unified dashboard existed
- Manual reporting across a 2TB dataset was bottlenecking delivery; reports were late and error-prone
- Leadership had no consistent weekly performance cadence — decisions were made without a shared data foundation
- Existing workflows had 6 identified failure points causing downstream data errors

---

## Solution

A two-part intervention:

1. **KPI Framework + Power BI Dashboard Suite** — a unified set of 5 dashboards consolidating all key performance dimensions into one reporting layer for leadership
2. **Pipeline Re-engineering** — rebuilt the underlying data workflows using Python and Apache Spark to eliminate the manual bottleneck and automate validation

---

## Dashboard Design

### KPI Framework
Three performance domains consolidated into a single view:

| Domain | Key Metrics |
|---|---|
| Churn Risk | Churn rate by segment, at-risk customer count, churn trend (MoM) |
| Revenue | Total revenue, revenue by product line, MoM and YoY variance |
| Network Performance | Uptime %, incident count, MTTR (mean time to resolve), region-level drill-down |

### Dashboard Suite (5 Dashboards)
| Dashboard | Audience | Purpose |
|---|---|---|
| Executive Summary | C-suite / Senior Leadership | Single-page weekly snapshot across all 3 domains |
| Churn Risk Monitor | Customer Success | Segment-level churn trends and at-risk flags |
| Revenue Tracker | Finance | Revenue performance vs. targets, by product and region |
| Network Operations | Network Team | Uptime, incidents, and SLA compliance |
| Cross-functional Trend View | All Teams | 13-week rolling trends across all KPIs |

### Iteration Process
- Presented initial prototype to 15+ senior stakeholders
- Ran 3 structured feedback cycles — each cycle produced a documented change log
- Formally adopted as the standard weekly reporting suite after cycle 3

---

## Pipeline Re-engineering

### The Problem
Manual reporting across the 2TB dataset required analysts to run extract, transform, and load steps by hand — 15 hours of effort per week, with frequent errors at 6 identified failure points.

### The Fix
Rebuilt the pipeline end-to-end using Python and Apache Spark:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lag
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("TelecomKPIPipeline").getOrCreate()

# Load raw telecom data
df = spark.read.parquet("s3://telecom-data/raw/")

# Churn risk scoring — flag customers with declining usage over 60 days
# Assumes one row per customer per day (lag offset = 60 rows = 60 days)
window = Window.partitionBy("customer_id").orderBy("date")
df = df.withColumn("prev_usage", lag("usage_gb", 60).over(window))
df = df.withColumn(
    "churn_risk_flag",
    when(col("usage_gb") < col("prev_usage") * 0.5, 1).otherwise(0)
)

# Write processed output
df.write.mode("overwrite").parquet("s3://telecom-data/processed/kpi_ready/")
```

### Automated Validation
Built validation checks to catch errors at each of the 6 identified failure points before data reached the dashboard layer:

```python
def validate_kpi_output(df):
    checks = {
        "no_null_customer_ids": df.filter(col("customer_id").isNull()).count() == 0,
        "revenue_non_negative": df.filter(col("revenue") < 0).count() == 0,
        "churn_flag_binary": df.filter(~col("churn_risk_flag").isin([0, 1])).count() == 0,
        "date_range_valid": df.filter(col("date") > "2022-06-30").count() == 0,
        "no_duplicate_records": df.count() == df.dropDuplicates(["customer_id", "date"]).count(),
        "usage_within_bounds": df.filter(col("usage_gb") > 10000).count() == 0,
    }
    failures = [k for k, v in checks.items() if not v]
    if failures:
        raise ValueError(f"Validation failed: {failures}")
    return True
```

All 6 failure points addressed — validated with business users before each release.

---

## Results

- **40% reduction** in end-to-end reporting cycle time
- **15 hours of manual effort eliminated** per week
- **25% reduction** in downstream data errors through automated validation
- **5 dashboards** built and presented to 15+ senior stakeholders
- **3 feedback cycles** completed — formally adopted as standard weekly reporting suite within 3 months

---

## Stack

- **Power BI Desktop** — dashboard design and data modelling
- **DAX** — calculated measures, time intelligence (MTD, QTD, YTD, rolling averages)
- **Python** — pipeline orchestration, validation logic, data transformation
- **Apache Spark (PySpark)** — distributed processing of 2TB telecom dataset
- **Parquet / S3** — data storage and transfer format

---

## DAX Measures (Key Examples)

```dax
// Rolling 13-week churn rate
Churn_Rate_13W =
DIVIDE(
    CALCULATE(
        COUNTROWS(Customers),
        FILTER(
            DATESINPERIOD('Date'[Date], LASTDATE('Date'[Date]), -91, DAY),
            Customers[churn_flag] = 1
        )
    ),
    CALCULATE(
        COUNTROWS(Customers),
        DATESINPERIOD('Date'[Date], LASTDATE('Date'[Date]), -91, DAY)
    ),
    0
)

// MoM revenue variance %
Revenue_MoM_Variance =
DIVIDE(
    [Total Revenue] - CALCULATE([Total Revenue], DATEADD('Date'[Date], -1, MONTH)),
    CALCULATE([Total Revenue], DATEADD('Date'[Date], -1, MONTH)),
    0
)
```

---

## File Structure

```
telecom-kpi-dashboard/
├── dashboards/
│   └── telecom_kpi_suite.pbix          # Power BI file (all 5 dashboards)
├── pipeline/
│   ├── extract.py                      # Raw data extraction
│   ├── transform.py                    # Spark-based transformations
│   ├── validate.py                     # Automated validation checks
│   └── load.py                         # Output to processed layer
├── notebooks/
│   └── kpi_framework_design.ipynb      # KPI selection and rationale
├── data/
│   └── sample_telecom_data.parquet     # Anonymised sample (subset)
├── screenshots/
│   ├── executive_summary.png
│   ├── churn_monitor.png
│   └── revenue_tracker.png
├── requirements.txt
└── README.md
```

---

## How to Run the Pipeline

```bash
git clone https://github.com/your-username/telecom-kpi-dashboard.git
cd telecom-kpi-dashboard

# Install dependencies
# requirements.txt includes: pyspark, pandas, pyarrow, pytest, jupyter
pip install -r requirements.txt

# Run the full pipeline
python pipeline/extract.py
python pipeline/transform.py
python pipeline/validate.py
python pipeline/load.py
```

To open the dashboard: download `dashboards/telecom_kpi_suite.pbix` and open in Power BI Desktop.

---

## How to Open the Dashboard

1. Download `dashboards/telecom_kpi_suite.pbix`
2. Open in Power BI Desktop (free download from Microsoft)
3. Connect to `data/sample_telecom_data.parquet` if prompted to refresh the data source

---

## Key Takeaways

- A KPI framework is only as good as the buy-in process behind it — running 3 structured feedback cycles before adoption meant the final suite reflected what leadership actually needed, not what an analyst assumed they needed
- Distributed processing (Spark) was non-negotiable at 2TB — a Pandas-based approach would have been unworkable; knowing when to reach for the right tool matters as much as knowing the tool
- Automated validation at every pipeline stage was the difference between a dashboard leadership trusted and one they second-guessed — catching errors before they surfaced in reports built credibility fast
