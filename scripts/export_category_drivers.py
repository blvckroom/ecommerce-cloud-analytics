"""Decompose May-June changes for the five largest declining categories."""

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
                with comparison as (
                    select
                        category_name,
                        coalesce(sum(merchandise_gmv) filter (
                            where purchase_month = date '2018-05-01'
                        ), 0) as may_gmv,
                        coalesce(sum(merchandise_gmv) filter (
                            where purchase_month = date '2018-06-01'
                        ), 0) as june_gmv,
                        coalesce(sum(delivered_orders) filter (
                            where purchase_month = date '2018-05-01'
                        ), 0) as may_orders,
                        coalesce(sum(delivered_orders) filter (
                            where purchase_month = date '2018-06-01'
                        ), 0) as june_orders,
                        coalesce(sum(item_count) filter (
                            where purchase_month = date '2018-05-01'
                        ), 0) as may_items,
                        coalesce(sum(item_count) filter (
                            where purchase_month = date '2018-06-01'
                        ), 0) as june_items
                    from marts.mart_category_monthly
                    where purchase_month in (
                        date '2018-05-01', date '2018-06-01'
                    )
                    group by category_name
                ),
                priority as (
                    select *
                    from comparison
                    where june_gmv < may_gmv
                    order by june_gmv - may_gmv, category_name
                    limit 5
                ),
                metrics as (
                    select
                        *,
                        may_gmv / nullif(may_orders, 0)
                            as may_category_value_per_order,
                        june_gmv / nullif(june_orders, 0)
                            as june_category_value_per_order,
                        may_gmv / nullif(may_items, 0)
                            as may_average_item_price,
                        june_gmv / nullif(june_items, 0)
                            as june_average_item_price,
                        may_items / nullif(may_orders, 0)
                            as may_items_per_order,
                        june_items / nullif(june_orders, 0)
                            as june_items_per_order
                    from priority
                )
                select
                    *,
                    june_gmv - may_gmv as gmv_change,
                    (june_orders - may_orders)
                        * (
                            june_category_value_per_order
                            + may_category_value_per_order
                        ) / 2 as order_volume_effect,
                    (
                        june_category_value_per_order
                        - may_category_value_per_order
                    ) * (june_orders + may_orders) / 2
                        as category_value_effect
                from metrics
                order by june_gmv - may_gmv, category_name
            """)
            rows = cursor.fetchall()

    for row in rows:
        effects = (
            row["order_volume_effect"],
            row["category_value_effect"],
        )
        if any(value is None for value in effects):
            raise ValueError(
                f"Insufficient data for decomposition: {row['category_name']}"
            )

        residual = row["gmv_change"] - sum(effects, Decimal("0"))
        if abs(residual) > Decimal("0.01"):
            raise ValueError(
                f"Decomposition mismatch: {row['category_name']}"
            )
        row["decomposition_residual"] = residual

    report = {
        "currency": "BRL",
        "comparison": "May to June 2018",
        "population": "delivered orders",
        "selection": "five largest absolute category GMV declines",
        "metric_definition": (
            "Category value per order includes only merchandise "
            "belonging to that category, not the entire basket."
        ),
        "limitations": (
            "Average item price changes can reflect product mix. "
            "Decomposition is arithmetic, not causal."
        ),
        "categories": rows,
        "decomposition_check": "PASS within BRL 0.01",
    }

    target = ROOT / "docs/category_drivers_may_june_2018.json"
    target.write_text(
        json.dumps(
            report, ensure_ascii=False, indent=2, default=serialize
        ) + "\n",
        encoding="utf-8",
    )

    for row in rows:
        print(f"\n{row['category_name']}")
        print(
            f"  GMV: {row['may_gmv']:.2f} -> {row['june_gmv']:.2f}"
            f" | Change: {row['gmv_change']:.2f}"
        )
        print(
            f"  Category orders: {row['may_orders']} -> "
            f"{row['june_orders']}"
        )
        print(
            f"  Category value/order: "
            f"{row['may_category_value_per_order']:.2f} -> "
            f"{row['june_category_value_per_order']:.2f}"
        )
        print(
            f"  Order effect: {row['order_volume_effect']:.2f}"
            f" | Category value effect: {row['category_value_effect']:.2f}"
        )
        print(
            f"  Items: {row['may_items']} -> {row['june_items']}"
            f" | Average item price: "
            f"{row['may_average_item_price']:.2f} -> "
            f"{row['june_average_item_price']:.2f}"
        )
        print(
            f"  Items/category order: "
            f"{row['may_items_per_order']:.3f} -> "
            f"{row['june_items_per_order']:.3f}"
        )

    print("\nCATEGORY DRIVER CHECK: PASS")
    print(f"Saved: {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except psycopg.Error as error:
        print("CATEGORY DRIVER EXPORT: FAILED")
        print(f"Error type: {type(error).__name__}")
        print(f"SQLSTATE: {error.sqlstate or 'not available'}")
        sys.exit(1)
