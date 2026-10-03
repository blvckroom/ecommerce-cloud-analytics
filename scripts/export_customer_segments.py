import json
import os
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


def serialize(value):
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Unsupported type: {type(value).__name__}")


overview_sql = """
select
    count(*) as customers,
    sum(frequency_orders) as delivered_orders,
    sum(monetary_gmv) as merchandise_gmv,
    count(*) filter (where frequency_orders >= 2) as repeat_customers
from marts.mart_customer_rfm
"""

segments_sql = """
with segments as (
    select
        customer_segment,
        count(*) as customers,
        sum(frequency_orders) as delivered_orders,
        sum(monetary_gmv) as merchandise_gmv,
        avg(monetary_gmv) as average_gmv_per_customer,
        avg(frequency_orders) as average_orders_per_customer,
        percentile_cont(0.5) within group (order by recency_days)
            as median_recency_days
    from marts.mart_customer_rfm
    group by customer_segment
)
select
    *,
    100.0 * customers / sum(customers) over () as customer_share_pct,
    100.0 * merchandise_gmv / nullif(
        sum(merchandise_gmv) over (), 0
    ) as gmv_share_pct,
    merchandise_gmv / nullif(delivered_orders, 0) as aov
from segments
order by merchandise_gmv desc
"""


def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is missing.")

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(overview_sql)
            overview = dict(cur.fetchone())
            cur.execute(segments_sql)
            segments = [dict(row) for row in cur.fetchall()]

    failures = []
    expected = {
        "customers": 86960,
        "delivered_orders": 89860,
        "merchandise_gmv": Decimal("12342450.49"),
        "repeat_customers": 2609,
    }
    for key, value in expected.items():
        if overview[key] != value:
            failures.append(f"Baseline mismatch: {key}.")

    for key in ("customers", "delivered_orders", "merchandise_gmv"):
        if sum(row[key] for row in segments) != overview[key]:
            failures.append(f"Segment total mismatch: {key}.")

    valid_segments = {
        "recent_repeat", "inactive_repeat",
        "recent_single", "inactive_single",
    }
    if not segments:
        failures.append("Segment results are empty.")
    if any(row["customer_segment"] not in valid_segments for row in segments):
        failures.append("Unexpected segment name.")
    if sum(
        row["customers"]
        for row in segments
        if row["customer_segment"] in ("recent_repeat", "inactive_repeat")
    ) != overview["repeat_customers"]:
        failures.append("Repeat segment totals do not reconcile.")

    if failures:
        raise RuntimeError("; ".join(failures))

    results = {
        "definitions": {
            "currency": "BRL",
            "population": "customers with delivered purchases within the window",
            "purchase_window": "[2017-01-01, 2018-08-01)",
            "reference_date": "2018-08-01",
            "recency": "calendar days since latest purchase within the window",
            "frequency": "delivered orders within the window",
            "monetary": "merchandise GMV within the window, excluding freight",
            "recent_threshold_days": 90,
            "repeat_threshold_orders": 2,
            "limitations": [
                "Segmentation thresholds are working assumptions.",
                "Inactive means no purchase in the latest 90 days, not confirmed churn.",
                "Frequency and monetary cover the analysis window, not lifetime history.",
                "Monetary is observed merchandise GMV, not profit or CLV.",
                "Final delivered status does not reconstruct status known on the reference date.",
            ],
        },
        "overview": overview,
        "segments": segments,
        "reconciliation": "PASS",
    }

    output = Path("docs/customer_segments.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=serialize)
        + "\n",
        encoding="utf-8",
    )

    print("CUSTOMER SEGMENT OVERVIEW")
    print(json.dumps(overview, indent=2, default=serialize))

    print("\nSEGMENT PERFORMANCE")
    for row in segments:
        print(f"\n{row['customer_segment']}")
        print(
            f"  Customers: {row['customers']:,}"
            f" | Share: {row['customer_share_pct']:.2f}%"
        )
        print(
            f"  GMV: {row['merchandise_gmv']:.2f} BRL"
            f" | Share: {row['gmv_share_pct']:.2f}%"
        )
        print(
            f"  Orders: {row['delivered_orders']}"
            f" | Orders/customer: {row['average_orders_per_customer']:.3f}"
        )
        print(
            f"  GMV/customer: {row['average_gmv_per_customer']:.2f} BRL"
            f" | AOV: {row['aov']:.2f} BRL"
        )
        print(f"  Median recency: {row['median_recency_days']:.1f} days")

    print("\nCUSTOMER SEGMENT RECONCILIATION: PASS")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
