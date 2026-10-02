"""Export verified sales KPIs and monthly GMV decomposition."""

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
    if hasattr(value, "isoformat"):
        return value.isoformat()
    raise TypeError(f"Unsupported type: {type(value).__name__}")


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
                    sum(merchandise_value) as merchandise_gmv,
                    count(*) as delivered_orders,
                    count(distinct customer_unique_id)
                        as purchasing_customers,
                    sum(merchandise_value) / nullif(count(*), 0) as aov
                from marts.fct_orders
                where order_status = 'delivered'
                  and purchased_at >= timestamp '2017-01-01'
                  and purchased_at < timestamp '2018-08-01'
            """)
            overview = cursor.fetchone()

            cursor.execute("""
                with previous as (
                    select
                        *,
                        lag(delivered_orders) over (
                            order by purchase_month
                        ) as previous_orders,
                        lag(aov) over (
                            order by purchase_month
                        ) as previous_aov
                    from marts.mart_sales_monthly
                ),
                effects as (
                    select
                        *,
                        merchandise_gmv - previous_month_gmv
                            as gmv_change,
                        (delivered_orders - previous_orders)
                            * (aov + previous_aov) / 2
                            as order_volume_effect,
                        (aov - previous_aov)
                            * (delivered_orders + previous_orders) / 2
                            as aov_effect
                    from previous
                )
                select
                    purchase_month,
                    merchandise_gmv,
                    delivered_orders,
                    purchasing_customers,
                    aov,
                    gmv_mom_growth_pct,
                    gmv_change,
                    order_volume_effect,
                    aov_effect,
                    gmv_change - order_volume_effect - aov_effect
                        as decomposition_residual
                from effects
                order by purchase_month
            """)
            monthly = cursor.fetchall()

    failures = [
        row["purchase_month"].isoformat()
        for row in monthly
        if row["decomposition_residual"] is not None
        and abs(row["decomposition_residual"]) > Decimal("0.01")
    ]
    if failures:
        raise ValueError(f"Decomposition mismatch: {failures}")

    report = {
        "currency": "BRL",
        "population": "delivered orders",
        "purchase_window": {
            "start_inclusive": "2017-01-01",
            "end_exclusive": "2018-08-01",
        },
        "overview": overview,
        "monthly": monthly,
        "decomposition_method": (
            "Symmetric two-factor decomposition of GMV = orders * AOV. "
            "This is an arithmetic attribution, not causal evidence."
        ),
        "decomposition_check": "PASS within BRL 0.01",
    }

    target = ROOT / "docs/sales_results.json"
    target.write_text(
        json.dumps(
            report, ensure_ascii=False, indent=2, default=serialize
        ) + "\n",
        encoding="utf-8",
    )

    print("SALES OVERVIEW")
    print(json.dumps(overview, indent=2, default=serialize))

    print("\nMONTHLY SALES AND DECOMPOSITION")
    for row in monthly:
        growth = row["gmv_mom_growth_pct"]
        growth_text = "N/A" if growth is None else f"{growth:.2f}%"
        print(
            f"{row['purchase_month']} | "
            f"GMV={row['merchandise_gmv']:.2f} | "
            f"Orders={row['delivered_orders']} | "
            f"Customers={row['purchasing_customers']} | "
            f"AOV={row['aov']:.2f} | MoM={growth_text}"
        )

        if row["gmv_change"] is not None:
            print(
                f"  GMV change={row['gmv_change']:.2f} | "
                f"Order effect={row['order_volume_effect']:.2f} | "
                f"AOV effect={row['aov_effect']:.2f}"
            )

    print("\nDECOMPOSITION CHECK: PASS")
    print(f"Saved: {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except psycopg.Error as error:
        print("SALES EXPORT: FAILED")
        print(f"Error type: {type(error).__name__}")
        print(f"SQLSTATE: {error.sqlstate or 'not available'}")
        sys.exit(1)
