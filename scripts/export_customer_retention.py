import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


def serialize(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Unsupported type: {type(value).__name__}")


overview_sql = """
with customer_orders as (
    select
        customer_unique_id,
        sum(delivered_orders) as delivered_orders
    from intermediate.int_customer_monthly
    where activity_month >= date '2017-01-01'
      and activity_month < date '2018-08-01'
    group by customer_unique_id
)
select
    count(*) as purchasing_customers,
    sum(delivered_orders) as delivered_orders,
    count(*) filter (where delivered_orders >= 2) as repeat_customers,
    100.0 * count(*) filter (where delivered_orders >= 2)
        / nullif(count(*), 0) as repeat_customer_rate_pct
from customer_orders
"""

frequency_sql = """
with customer_orders as (
    select
        customer_unique_id,
        sum(delivered_orders) as delivered_orders
    from intermediate.int_customer_monthly
    where activity_month >= date '2017-01-01'
      and activity_month < date '2018-08-01'
    group by customer_unique_id
)
select
    delivered_orders as orders_per_customer,
    count(*) as customers
from customer_orders
group by delivered_orders
order by delivered_orders
"""

cohort_sql = """
select
    cohort_month,
    month_number,
    activity_month,
    cohort_customers,
    is_observed,
    active_customers,
    retention_pct
from marts.mart_customer_cohort
order by cohort_month, month_number
"""

pooled_sql = """
select
    month_number,
    count(*) as observed_cohorts,
    sum(cohort_customers) as eligible_cohort_customers,
    sum(active_customers) as active_customers,
    100.0 * sum(active_customers)
        / nullif(sum(cohort_customers), 0) as weighted_retention_pct
from marts.mart_customer_cohort
where cohort_month >= date '2017-01-01'
  and is_observed
group by month_number
order by month_number
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

            cur.execute(frequency_sql)
            frequency = [dict(row) for row in cur.fetchall()]

            cur.execute(cohort_sql)
            cohorts = [dict(row) for row in cur.fetchall()]

            cur.execute(pooled_sql)
            pooled = [dict(row) for row in cur.fetchall()]

    failures = []
    if overview["purchasing_customers"] != 86960:
        failures.append("Customer count differs from sales baseline.")
    if overview["delivered_orders"] != 89860:
        failures.append("Order count differs from sales baseline.")

    if sum(row["customers"] for row in frequency) != 86960:
        failures.append("Frequency customer totals do not reconcile.")
    if sum(
        row["orders_per_customer"] * row["customers"]
        for row in frequency
    ) != 89860:
        failures.append("Frequency order totals do not reconcile.")
    if sum(
        row["customers"]
        for row in frequency
        if row["orders_per_customer"] >= 2
    ) != overview["repeat_customers"]:
        failures.append("Repeat customer totals do not reconcile.")

    if not cohorts or not pooled:
        failures.append("Cohort results are empty.")

    for row in cohorts:
        if not row["is_observed"]:
            if (
                row["active_customers"] is not None
                or row["retention_pct"] is not None
            ):
                failures.append("Unobserved month contains retention values.")
        elif row["month_number"] == 0:
            if (
                row["active_customers"] != row["cohort_customers"]
                or row["retention_pct"] != Decimal("100")
            ):
                failures.append("Month-zero retention is not 100%.")

    if failures:
        raise RuntimeError("; ".join(failures))

    results = {
        "definitions": {
            "customer_identity": "customer_unique_id",
            "population": "delivered orders; final snapshot status",
            "repeat_window": "[2017-01-01, 2018-08-01)",
            "repeat_customer": "at least two delivered orders within repeat window",
            "cohort": "first observed delivered purchase month using all history before 2018-08-01",
            "monthly_retention": "customers active in month M / original cohort customers",
            "horizon": "M0 through M12",
            "unobserved_months": "NULL, not zero",
            "weighted_retention": "sum active customers / sum cohort customers across eligible cohorts starting in 2017",
            "limitations": [
                "First observed purchase may not be the customer's first lifetime purchase.",
                "Repeat rate depends on the observation window.",
                "Eligible cohort composition changes across retention horizons.",
                "Monthly retention is not cumulative and need not decrease monotonically.",
            ],
        },
        "overview": overview,
        "purchase_frequency": frequency,
        "cohort_retention": cohorts,
        "weighted_retention_by_horizon": pooled,
        "reconciliation": "PASS",
    }

    output = Path("docs/customer_retention.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=serialize)
        + "\n",
        encoding="utf-8",
    )

    print("CUSTOMER OVERVIEW")
    print(json.dumps(overview, indent=2, default=serialize))

    print("\nPURCHASE FREQUENCY")
    for row in frequency:
        print(
            f"{row['orders_per_customer']} orders/customer"
            f" | Customers={row['customers']}"
        )

    print("\nCOHORT RETENTION — SELECTED HORIZONS")
    for row in cohorts:
        if (
            row["cohort_month"] >= date(2017, 1, 1)
            and row["month_number"] in (1, 3, 6, 12)
        ):
            retention = (
                f"{row['retention_pct']:.4f}%"
                if row["is_observed"]
                else "N/A — unobserved"
            )
            print(
                f"{row['cohort_month']} | M{row['month_number']}"
                f" | Cohort={row['cohort_customers']}"
                f" | Active={row['active_customers']}"
                f" | Retention={retention}"
            )

    print("\nWEIGHTED RETENTION — OBSERVED COHORTS STARTING IN 2017")
    for row in pooled:
        print(
            f"M{row['month_number']}"
            f" | Cohorts={row['observed_cohorts']}"
            f" | Eligible customers={row['eligible_cohort_customers']}"
            f" | Active={row['active_customers']}"
            f" | Retention={row['weighted_retention_pct']:.4f}%"
        )

    print("\nCUSTOMER RETENTION RECONCILIATION: PASS")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
