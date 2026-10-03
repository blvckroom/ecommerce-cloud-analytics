"""Analyze category contributions to May-June 2018 GMV changes."""

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
                with may as (
                    select category_name, merchandise_gmv
                    from marts.mart_category_monthly
                    where purchase_month = date '2018-05-01'
                ),
                june as (
                    select category_name, merchandise_gmv
                    from marts.mart_category_monthly
                    where purchase_month = date '2018-06-01'
                )
                select
                    coalesce(m.category_name, j.category_name)
                        as category_name,
                    coalesce(m.merchandise_gmv, 0) as may_gmv,
                    coalesce(j.merchandise_gmv, 0) as june_gmv,
                    coalesce(j.merchandise_gmv, 0)
                        - coalesce(m.merchandise_gmv, 0) as gmv_change
                from may m
                full outer join june j using (category_name)
                order by gmv_change, category_name
            """)
            categories = cursor.fetchall()

            cursor.execute("""
                select
                    (select merchandise_gmv
                     from marts.mart_sales_monthly
                     where purchase_month = date '2018-06-01')
                    -
                    (select merchandise_gmv
                     from marts.mart_sales_monthly
                     where purchase_month = date '2018-05-01')
                    as total_gmv_change
            """)
            total_change = cursor.fetchone()["total_gmv_change"]

    category_change = sum(
        (row["gmv_change"] for row in categories), Decimal("0")
    )

    if category_change != total_change:
        raise ValueError("Category changes do not reconcile to sales")

    gross_decline = sum(
        (-row["gmv_change"] for row in categories
         if row["gmv_change"] < 0),
        Decimal("0"),
    )
    gross_increase = sum(
        (row["gmv_change"] for row in categories
         if row["gmv_change"] > 0),
        Decimal("0"),
    )

    for row in categories:
        row["gmv_growth_pct"] = (
            row["gmv_change"] / row["may_gmv"] * 100
            if row["may_gmv"] else None
        )
        row["share_of_gross_decline_pct"] = (
            -row["gmv_change"] / gross_decline * 100
            if row["gmv_change"] < 0 and gross_decline else None
        )

    declining = [
        row for row in categories if row["gmv_change"] < 0
    ]
    increasing = sorted(
        (row for row in categories if row["gmv_change"] > 0),
        key=lambda row: (-row["gmv_change"], row["category_name"]),
    )

    top_five_decline = sum(
        (-row["gmv_change"] for row in declining[:5]), Decimal("0")
    )

    summary = {
        "currency": "BRL",
        "comparison": "May to June 2018",
        "population": "delivered orders",
        "net_gmv_change": total_change,
        "gross_decline": gross_decline,
        "gross_increase": gross_increase,
        "declining_categories": len(declining),
        "increasing_categories": len(increasing),
        "top_five_share_of_gross_decline_pct": (
            top_five_decline / gross_decline * 100
            if gross_decline else None
        ),
        "reconciliation": "PASS",
    }

    report = {"summary": summary, "categories": categories}
    target = ROOT / "docs/category_changes_may_june_2018.json"
    target.write_text(
        json.dumps(
            report, ensure_ascii=False, indent=2, default=serialize
        ) + "\n",
        encoding="utf-8",
    )

    print("CATEGORY CHANGE SUMMARY")
    print(json.dumps(summary, indent=2, default=serialize))

    print("\nTOP 10 DECLINING CATEGORIES")
    for row in declining[:10]:
        print(
            f"{row['category_name']} | "
            f"May={row['may_gmv']:.2f} | "
            f"June={row['june_gmv']:.2f} | "
            f"Change={row['gmv_change']:.2f} | "
            f"Growth={row['gmv_growth_pct']:.2f}% | "
            f"Gross decline share="
            f"{row['share_of_gross_decline_pct']:.2f}%"
        )

    print("\nTOP 10 INCREASING CATEGORIES")
    for row in increasing[:10]:
        growth = row["gmv_growth_pct"]
        growth_text = "N/A" if growth is None else f"{growth:.2f}%"
        print(
            f"{row['category_name']} | "
            f"May={row['may_gmv']:.2f} | "
            f"June={row['june_gmv']:.2f} | "
            f"Change=+{row['gmv_change']:.2f} | "
            f"Growth={growth_text}"
        )

    print("\nCATEGORY RECONCILIATION: PASS")
    print(f"Saved: {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except psycopg.Error as error:
        print("CATEGORY EXPORT: FAILED")
        print(f"Error type: {type(error).__name__}")
        print(f"SQLSTATE: {error.sqlstate or 'not available'}")
        sys.exit(1)
