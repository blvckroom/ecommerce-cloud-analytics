"""Check monetary values, review selection and observation boundaries."""

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/olist"


def read_csv(name):
    with (SOURCE / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def check_money(rows, column):
    invalid = missing = negative = zero = 0
    total = Decimal("0")
    minimum = maximum = None

    for row in rows:
        value = row[column].strip()
        if not value:
            missing += 1
            continue
        try:
            number = Decimal(value)
            if not number.is_finite():
                raise InvalidOperation
        except InvalidOperation:
            invalid += 1
            continue

        total += number
        negative += number < 0
        zero += number == 0
        minimum = number if minimum is None else min(minimum, number)
        maximum = number if maximum is None else max(maximum, number)

    return {
        "missing": missing,
        "invalid": invalid,
        "negative": negative,
        "zero": zero,
        "minimum": str(minimum) if minimum is not None else None,
        "maximum": str(maximum) if maximum is not None else None,
        "sum": str(total),
    }


def review_rank(row):
    # Missing timestamps rank before valid timestamps.
    return (
        row["review_answer_timestamp"],
        row["review_creation_date"],
        row["review_id"],
    )


def main():
    orders = read_csv("olist_orders_dataset.csv")
    items = read_csv("olist_order_items_dataset.csv")
    payments = read_csv("olist_order_payments_dataset.csv")
    reviews = read_csv("olist_order_reviews_dataset.csv")

    money_checks = {
        "item_price": check_money(items, "price"),
        "item_freight": check_money(items, "freight_value"),
        "payment_value": check_money(payments, "payment_value"),
    }

    review_groups = defaultdict(list)
    review_ids = Counter()
    invalid_scores = 0

    for row in reviews:
        review_groups[row["order_id"]].append(row)
        review_ids[row["review_id"]] += 1
        if row["review_score"] not in {"1", "2", "3", "4", "5"}:
            invalid_scores += 1

    conflicting_scores = 0
    rank_tie_orders = 0
    unresolved_tie_orders = 0
    selected = {}

    for order_id, group in review_groups.items():
        if len({row["review_score"] for row in group}) > 1:
            conflicting_scores += 1

        highest_rank = max(review_rank(row) for row in group)
        tied = [row for row in group if review_rank(row) == highest_rank]

        if len(tied) > 1:
            rank_tie_orders += 1
            if len({row["review_score"] for row in tied}) > 1:
                unresolved_tie_orders += 1

        selected[order_id] = tied[0]

    delivered = [
        row for row in orders if row["order_status"] == "delivered"
    ]
    purchase_times = [
        datetime.fromisoformat(row["order_purchase_timestamp"])
        for row in delivered
    ]
    august_daily = Counter(
        row["order_purchase_timestamp"][:10]
        for row in delivered
        if row["order_purchase_timestamp"].startswith("2018-08")
    )

    review_before_delivery = 0
    review_delivery_comparable = 0

    for row in delivered:
        review = selected.get(row["order_id"])
        actual = row["order_delivered_customer_date"]

        if review and actual and review["review_answer_timestamp"]:
            review_delivery_comparable += 1
            answer = datetime.fromisoformat(
                review["review_answer_timestamp"]
            )
            delivery = datetime.fromisoformat(actual)
            review_before_delivery += answer < delivery

    item_totals = defaultdict(lambda: Decimal("0"))
    payment_totals = defaultdict(lambda: Decimal("0"))

    # Reconciliation requires valid finite monetary values.
    invalid_money = any(
        result["missing"] or result["invalid"]
        for result in money_checks.values()
    )

    reconciliation = {"status": "skipped due to invalid or missing money"}

    if not invalid_money:
        for row in items:
            item_totals[row["order_id"]] += (
                Decimal(row["price"]) + Decimal(row["freight_value"])
            )
        for row in payments:
            payment_totals[row["order_id"]] += Decimal(
                row["payment_value"]
            )

        differences = []
        for row in delivered:
            order_id = row["order_id"]
            if order_id in item_totals and order_id in payment_totals:
                differences.append(
                    payment_totals[order_id] - item_totals[order_id]
                )

        reconciliation = {
            "status": "completed",
            "compared_delivered_orders": len(differences),
            "absolute_difference_over_0_01": sum(
                abs(value) > Decimal("0.01") for value in differences
            ),
            "absolute_difference_over_1_00": sum(
                abs(value) > Decimal("1.00") for value in differences
            ),
            "sum_payment_minus_items_and_freight": str(
                sum(differences, Decimal("0"))
            ),
        }

    report = {
        "money_checks_all_source_rows": money_checks,
        "review_checks": {
            "invalid_score_rows": invalid_scores,
            "missing_review_id_rows": review_ids.get("", 0),
            "review_ids_used_more_than_once": sum(
                count > 1 for key, count in review_ids.items() if key
            ),
            "orders_with_conflicting_review_scores": conflicting_scores,
            "orders_with_top_rank_ties": rank_tie_orders,
            "orders_with_top_rank_conflicting_scores": unresolved_tie_orders,
            "selection_candidate": (
                "latest answer timestamp, then creation timestamp, "
                "then review_id"
            ),
            "delivered_orders_with_review_and_delivery_timestamps":
                review_delivery_comparable,
            "selected_review_answer_before_actual_delivery":
                review_before_delivery,
        },
        "delivered_purchase_boundary": {
            "first": min(purchase_times).isoformat(),
            "last": max(purchase_times).isoformat(),
            "august_2018_daily_orders": dict(sorted(august_daily.items())),
        },
        "payment_reconciliation": reconciliation,
    }

    target = ROOT / "docs/analysis_rule_checks.json"
    target.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("\nANALYSIS RULE CHECK: COMPLETE")


if __name__ == "__main__":
    main()
