"""Reconcile Neon raw tables against source profiling results."""

import json
import os
import sys
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]

TABLES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

RELATIONSHIPS = {
    "orders_customer": (
        "orders", "customer_id", "customers", "customer_id"
    ),
    "items_order": (
        "order_items", "order_id", "orders", "order_id"
    ),
    "items_product": (
        "order_items", "product_id", "products", "product_id"
    ),
    "items_seller": (
        "order_items", "seller_id", "sellers", "seller_id"
    ),
    "payments_order": (
        "payments", "order_id", "orders", "order_id"
    ),
    "reviews_order": (
        "reviews", "order_id", "orders", "order_id"
    ),
}


def main():
    profile = json.loads(
        (ROOT / "docs/source_profile.json").read_text(encoding="utf-8")
    )
    rules = json.loads(
        (ROOT / "docs/analysis_rule_checks.json").read_text(
            encoding="utf-8"
        )
    )
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL: MISSING")
        return 1

    report = {"rows": {}, "money": {}, "relationships": {}}
    failures = []

    with psycopg.connect(
        database_url,
        connect_timeout=30,
        options=(
            "-c default_transaction_read_only=on "
            "-c statement_timeout=60000"
        ),
    ) as connection:
        with connection.cursor() as cursor:
            for table, filename in TABLES.items():
                cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier("raw", table)
                    )
                )
                actual = cursor.fetchone()[0]
                expected = profile[filename]["rows"]
                report["rows"][table] = {
                    "expected": expected,
                    "actual": actual,
                    "pass": actual == expected,
                }
                if actual != expected:
                    failures.append(f"Row count: {table}")

            for label, table, column in [
                ("item_price", "order_items", "price"),
                ("item_freight", "order_items", "freight_value"),
                ("payment_value", "payments", "payment_value"),
            ]:
                cursor.execute(
                    sql.SQL("SELECT SUM({}) FROM {}").format(
                        sql.Identifier(column),
                        sql.Identifier("raw", table),
                    )
                )
                actual = cursor.fetchone()[0]
                expected = Decimal(
                    rules["money_checks_all_source_rows"][label]["sum"]
                )
                report["money"][label] = {
                    "expected": str(expected),
                    "actual": str(actual),
                    "pass": actual == expected,
                }
                if actual != expected:
                    failures.append(f"Money total: {label}")

            for label, (
                child, child_key, parent, parent_key
            ) in RELATIONSHIPS.items():
                cursor.execute(
                    sql.SQL("""
                        SELECT COUNT(*)
                        FROM {} AS c
                        LEFT JOIN {} AS p ON c.{} = p.{}
                        WHERE p.{} IS NULL
                    """).format(
                        sql.Identifier("raw", child),
                        sql.Identifier("raw", parent),
                        sql.Identifier(child_key),
                        sql.Identifier(parent_key),
                        sql.Identifier(parent_key),
                    )
                )
                orphans = cursor.fetchone()[0]
                report["relationships"][label] = {
                    "orphan_rows": orphans,
                    "pass": orphans == 0,
                }
                if orphans:
                    failures.append(f"Relationship: {label}")

            cursor.execute("""
                SELECT order_status, COUNT(*)
                FROM raw.orders
                GROUP BY order_status
                ORDER BY order_status
            """)
            actual_statuses = dict(cursor.fetchall())
            expected_statuses = profile[
                "olist_orders_dataset.csv"
            ]["order_status_counts"]

            report["status_counts"] = actual_statuses
            if actual_statuses != expected_statuses:
                failures.append("Order status counts")

            cursor.execute("""
                SELECT pg_size_pretty(
                    pg_database_size(current_database())
                )
            """)
            report["database_size"] = cursor.fetchone()[0]

    report["failures"] = failures
    report["pass"] = not failures

    target = ROOT / "docs/raw_validation.json"
    target.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("\nRAW VALIDATION:", "PASS" if not failures else "FAIL")
    return 0 if not failures else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except psycopg.Error as error:
        print("RAW VALIDATION: ERROR")
        print(f"Error type: {type(error).__name__}")
        print(f"SQLSTATE: {error.sqlstate or 'not available'}")
        sys.exit(1)
