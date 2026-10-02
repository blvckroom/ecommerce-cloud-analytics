"""Check relationships and analytical coverage without changing source data."""

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/olist"


def read_csv(name):
    with (SOURCE / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def missing(value):
    return not value or not value.strip()


def parse(value):
    return None if missing(value) else datetime.fromisoformat(value)


def main():
    orders = read_csv("olist_orders_dataset.csv")
    customers = read_csv("olist_customers_dataset.csv")
    items = read_csv("olist_order_items_dataset.csv")
    payments = read_csv("olist_order_payments_dataset.csv")
    reviews = read_csv("olist_order_reviews_dataset.csv")
    products = read_csv("olist_products_dataset.csv")
    sellers = read_csv("olist_sellers_dataset.csv")
    translations = read_csv("product_category_name_translation.csv")

    order_ids = {row["order_id"] for row in orders}
    customer_map = {row["customer_id"]: row for row in customers}
    product_ids = {row["product_id"] for row in products}
    seller_ids = {row["seller_id"] for row in sellers}
    item_order_ids = {row["order_id"] for row in items}
    payment_order_ids = {row["order_id"] for row in payments}
    review_order_ids = {row["order_id"] for row in reviews}
    translated_categories = {
        row["product_category_name"] for row in translations
    }

    relationships = {
        "orders_with_unknown_customer": sum(
            row["customer_id"] not in customer_map for row in orders
        ),
        "items_with_unknown_order": sum(
            row["order_id"] not in order_ids for row in items
        ),
        "items_with_unknown_product": sum(
            row["product_id"] not in product_ids for row in items
        ),
        "items_with_unknown_seller": sum(
            row["seller_id"] not in seller_ids for row in items
        ),
        "payments_with_unknown_order": sum(
            row["order_id"] not in order_ids for row in payments
        ),
        "reviews_with_unknown_order": sum(
            row["order_id"] not in order_ids for row in reviews
        ),
    }

    delivered = [
        row for row in orders if row["order_status"] == "delivered"
    ]
    customer_orders = Counter()
    monthly_all = Counter()
    monthly_delivered = Counter()
    missing_delivered_dates = Counter()
    negative_durations = Counter()
    late_orders = 0
    eligible_late_orders = 0
    unmapped_delivered_customers = 0

    for row in orders:
        purchase = parse(row["order_purchase_timestamp"])
        if purchase:
            monthly_all[purchase.strftime("%Y-%m")] += 1

    for row in delivered:
        customer = customer_map.get(row["customer_id"])
        unique_id = customer.get("customer_unique_id") if customer else None

        if missing(unique_id):
            unmapped_delivered_customers += 1
        else:
            customer_orders[unique_id] += 1

        purchase = parse(row["order_purchase_timestamp"])
        actual = parse(row["order_delivered_customer_date"])
        estimated = parse(row["order_estimated_delivery_date"])
        carrier = parse(row["order_delivered_carrier_date"])
        approved = parse(row["order_approved_at"])

        if purchase:
            monthly_delivered[purchase.strftime("%Y-%m")] += 1

        for column in (
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ):
            if missing(row[column]):
                missing_delivered_dates[column] += 1

        comparisons = {
            "approval_before_purchase": (approved, purchase),
            "carrier_before_purchase": (carrier, purchase),
            "delivery_before_purchase": (actual, purchase),
            "delivery_before_carrier": (actual, carrier),
        }
        for label, (end, start) in comparisons.items():
            if end and start and end < start:
                negative_durations[label] += 1

        if actual and estimated:
            eligible_late_orders += 1
            late_orders += actual.date() > estimated.date()

    frequency = Counter(customer_orders.values())
    repeat_customers = sum(
        count >= 2 for count in customer_orders.values()
    )
    category_missing = sum(
        missing(row["product_category_name"]) for row in products
    )
    unmapped_categories = sorted({
        row["product_category_name"]
        for row in products
        if not missing(row["product_category_name"])
        and row["product_category_name"] not in translated_categories
    })

    report = {
        "relationship_checks": relationships,
        "delivered_coverage": {
            "orders": len(delivered),
            "without_items": sum(
                row["order_id"] not in item_order_ids for row in delivered
            ),
            "without_payments": sum(
                row["order_id"] not in payment_order_ids for row in delivered
            ),
            "without_reviews": sum(
                row["order_id"] not in review_order_ids for row in delivered
            ),
            "missing_dates": dict(missing_delivered_dates),
            "negative_time_flags": dict(negative_durations),
            "eligible_late_orders": eligible_late_orders,
            "late_orders": late_orders,
            "late_rate_pct": (
                round(100 * late_orders / eligible_late_orders, 4)
                if eligible_late_orders else None
            ),
        },
        "customer_purchase_frequency": {
            "unmapped_delivered_orders": unmapped_delivered_customers,
            "purchasing_customers": len(customer_orders),
            "repeat_customers": repeat_customers,
            "repeat_rate_pct": (
                round(100 * repeat_customers / len(customer_orders), 4)
                if customer_orders else None
            ),
            "customers_by_delivered_order_count": {
                str(count): frequency[count] for count in sorted(frequency)
            },
        },
        "category_checks": {
            "products_missing_category": category_missing,
            "categories_without_translation": unmapped_categories,
        },
        "monthly_orders": [
            {
                "month": month,
                "all_orders": monthly_all[month],
                "delivered_orders": monthly_delivered[month],
            }
            for month in sorted(monthly_all)
        ],
    }

    target = ROOT / "docs/relationship_checks.json"
    target.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("\nRELATIONSHIP CHECK: COMPLETE")
    print("Created docs/relationship_checks.json")


if __name__ == "__main__":
    main()
