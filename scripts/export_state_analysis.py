"""Export state sales changes and delivery coverage."""

import json
import os
import sys
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]


def serialize(value):
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Unsupported type: {type(value).__name__}")


def percent(numerator, denominator):
    return (
        Decimal(numerator) / Decimal(denominator) * 100
        if denominator else None
    )


def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL: MISSING")
        return 1

    with psycopg.connect(
        database_url,
        connect_timeout=30,
        row_factory=dict_row,
        options=(
            "-c default_transaction_read_only=on "
            "-c statement_timeout=60000"
        ),
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                select
                    customer_state,
                    coalesce(sum(merchandise_gmv) filter (
                        where purchase_month = date '2018-05-01'
                    ), 0) as may_gmv,
                    coalesce(sum(merchandise_gmv) filter (
                        where purchase_month = date '2018-06-01'
                    ), 0) as june_gmv
                from marts.mart_state_monthly
                where purchase_month in (
                    date '2018-05-01', date '2018-06-01'
                )
                group by customer_state
            """)
            changes = cursor.fetchall()

            cursor.execute("""
                select
                    customer_state,
                    sum(merchandise_gmv) as merchandise_gmv,
                    sum(delivered_orders) as delivered_orders,
                    sum(delivery_date_eligible_orders)
                        as delivery_date_eligible_orders,
                    sum(late_orders) as late_orders
                from marts.mart_state_monthly
                group by customer_state
                order by merchandise_gmv desc, customer_state
            """)
            states = cursor.fetchall()

            cursor.execute("""
                select
                    sum(merchandise_value) as merchandise_gmv,
                    count(*) as delivered_orders,
                    count(*) filter (
                        where is_late_delivery is not null
                    ) as delivery_date_eligible_orders,
                    count(*) filter (
                        where is_late_delivery is true
                    ) as late_orders
                from marts.fct_orders
                where order_status = 'delivered'
                  and purchased_at >= timestamp '2017-01-01'
                  and purchased_at < timestamp '2018-08-01'
            """)
            overview = cursor.fetchone()

            cursor.execute("""
                select
                    (select merchandise_gmv
                     from marts.mart_sales_monthly
                     where purchase_month = date '2018-06-01')
                    -
                    (select merchandise_gmv
                     from marts.mart_sales_monthly
                     where purchase_month = date '2018-05-01')
                    as gmv_change
            """)
            expected_change = cursor.fetchone()["gmv_change"]

    for row in changes:
        row["gmv_change"] = row["june_gmv"] - row["may_gmv"]
        row["growth_pct"] = percent(
            row["gmv_change"], row["may_gmv"]
        )

    changes.sort(key=lambda row: (
        row["gmv_change"], row["customer_state"]
    ))

    actual_change = sum(
        (row["gmv_change"] for row in changes), Decimal("0")
    )
    if actual_change != expected_change:
        raise ValueError("State GMV changes do not reconcile")

    for field in (
        "merchandise_gmv",
        "delivered_orders",
        "delivery_date_eligible_orders",
        "late_orders",
    ):
        actual = sum(
            (row[field] for row in states), Decimal("0")
        )
        if actual != overview[field]:
            raise ValueError(f"State totals do not reconcile: {field}")

    for row in states:
        row["gmv_share_pct"] = percent(
            row["merchandise_gmv"], overview["merchandise_gmv"]
        )
        row["late_rate_pct"] = percent(
            row["late_orders"], row["delivery_date_eligible_orders"]
        )
        row["delivery_date_coverage_pct"] = percent(
            row["delivery_date_eligible_orders"], row["delivered_orders"]
        )

    overview["late_rate_pct"] = percent(
        overview["late_orders"],
        overview["delivery_date_eligible_orders"],
    )

    report = {
        "currency": "BRL",
        "population": "delivered orders",
        "purchase_window": "2017-01-01 inclusive to 2018-08-01 exclusive",
        "geography": "customer state associated with each order",
        "overview": overview,
        "may_june_changes": changes,
        "state_performance": states,
        "reconciliation": "PASS",
        "limitations": (
            "Sales changes and delivery rates are descriptive. "
            "They do not establish that late delivery caused sales decline."
        ),
    }

    target = ROOT / "docs/state_analysis.json"
    target.write_text(
        json.dumps(
            report, ensure_ascii=False, indent=2, default=serialize
        ) + "\n",
        encoding="utf-8",
    )

    print("STATE OVERVIEW")
    print(json.dumps(overview, indent=2, default=serialize))

    print("\nMAY TO JUNE GMV CHANGES — ALL STATES")
    for row in changes:
        growth = row["growth_pct"]
        growth_text = "N/A" if growth is None else f"{growth:.2f}%"
        print(
            f"{row['customer_state']} | "
            f"May={row['may_gmv']:.2f} | "
            f"June={row['june_gmv']:.2f} | "
            f"Change={row['gmv_change']:.2f} | "
            f"Growth={growth_text}"
        )

    print("\nFULL-WINDOW STATE PERFORMANCE — GMV DESCENDING")
    for row in states:
        late = row["late_rate_pct"]
        late_text = "N/A" if late is None else f"{late:.2f}%"
        print(
            f"{row['customer_state']} | "
            f"GMV={row['merchandise_gmv']:.2f} | "
            f"GMV share={row['gmv_share_pct']:.2f}% | "
            f"Orders={row['delivered_orders']} | "
            f"Eligible={row['delivery_date_eligible_orders']} | "
            f"Late={row['late_orders']} | "
            f"Late rate={late_text}"
        )

    print("\nSTATE RECONCILIATION: PASS")
    print(f"Saved: {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except psycopg.Error as error:
        print("STATE EXPORT: FAILED")
        print(f"Error type: {type(error).__name__}")
        print(f"SQLSTATE: {error.sqlstate or 'not available'}")
        sys.exit(1)
