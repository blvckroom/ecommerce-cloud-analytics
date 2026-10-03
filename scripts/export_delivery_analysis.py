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
    count(*) as delivered_orders,
    count(*) filter (where delivery_date_eligible) as eligible_orders,
    count(*) filter (where not delivery_date_eligible) as ineligible_orders,
    count(*) filter (where is_late_delivery) as late_orders,
    100.0 * count(*) filter (where is_late_delivery)
        / nullif(count(*) filter (where delivery_date_eligible), 0)
        as late_rate_pct,
    count(delivery_days) as delivery_duration_eligible_orders,
    percentile_cont(0.5) within group (order by delivery_days)
        as median_delivery_days,
    percentile_cont(0.9) within group (order by delivery_days)
        as p90_delivery_days,
    percentile_cont(0.5) within group (order by days_late)
        filter (where is_late_delivery) as median_days_late,
    percentile_cont(0.9) within group (order by days_late)
        filter (where is_late_delivery) as p90_days_late,
    count(review_score) as orders_with_selected_review,
    count(*) filter (where missing_review) as orders_without_review,
    count(*) filter (where review_answer_before_delivery)
        as review_answers_before_delivery
from marts.mart_delivery_orders
"""

rating_sql = """
select
    case when is_late_delivery then 'late' else 'on_time' end
        as delivery_group,
    count(*) as orders,
    count(review_score) as reviewed_orders,
    avg(review_score) as average_review_score,
    count(*) filter (where is_low_rating) as low_rating_orders,
    100.0 * count(*) filter (where is_low_rating)
        / nullif(count(review_score), 0) as low_rating_pct,
    percentile_cont(0.5) within group (order by delivery_days)
        as median_delivery_days,
    percentile_cont(0.5) within group (order by promised_delivery_days)
        as median_promised_delivery_days
from marts.mart_delivery_orders
where delivery_date_eligible
{extra_filter}
group by is_late_delivery
order by is_late_delivery
"""

state_sql = """
select
    customer_state,
    count(*) as delivered_orders,
    count(*) filter (where delivery_date_eligible) as eligible_orders,
    count(*) filter (where is_late_delivery) as late_orders,
    100.0 * count(*) filter (where is_late_delivery)
        / nullif(count(*) filter (where delivery_date_eligible), 0)
        as late_rate_pct,
    percentile_cont(0.5) within group (order by delivery_days)
        as median_delivery_days,
    percentile_cont(0.9) within group (order by delivery_days)
        as p90_delivery_days,
    percentile_cont(0.5) within group (order by promised_delivery_days)
        as median_promised_delivery_days,
    percentile_cont(0.5) within group (order by days_late)
        filter (where is_late_delivery) as median_days_late
from marts.mart_delivery_orders
where customer_state in ('SP', 'RJ')
group by customer_state
order by customer_state
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

            cur.execute(rating_sql.format(extra_filter=""))
            all_reviews = [dict(row) for row in cur.fetchall()]

            cur.execute(rating_sql.format(
                extra_filter="and review_answered_at >= delivered_at"
            ))
            after_delivery = [dict(row) for row in cur.fetchall()]

            cur.execute(state_sql)
            states = [dict(row) for row in cur.fetchall()]

    failures = []
    if overview["delivered_orders"] != 89860:
        failures.append("Delivered order count differs from sales baseline.")
    if overview["eligible_orders"] != 89852:
        failures.append("Eligible order count differs from state baseline.")
    if overview["late_orders"] != 6138:
        failures.append("Late order count differs from state baseline.")
    if sum(row["orders"] for row in all_reviews) != overview["eligible_orders"]:
        failures.append("Delivery groups do not reconcile to eligible orders.")

    for label, groups in [
        ("all_selected_reviews", all_reviews),
        ("answered_after_delivery", after_delivery),
    ]:
        for row in groups:
            if not (
                0 <= row["low_rating_orders"]
                <= row["reviewed_orders"]
                <= row["orders"]
            ):
                failures.append(f"Invalid review counts: {label}.")

    if failures:
        raise RuntimeError("; ".join(failures))

    results = {
        "scope": {
            "population": "delivered orders",
            "purchase_start_inclusive": "2017-01-01",
            "purchase_end_exclusive": "2018-08-01",
            "late_definition": "actual delivery date > estimated delivery date",
            "low_rating_definition": "selected review score in (1, 2)",
            "interpretation": "descriptive association, not causal evidence",
            "sensitivity": (
                "selected review answer timestamp >= actual delivery timestamp; "
                "this does not establish when the review was first created"
            ),
        },
        "overview": overview,
        "ratings_all_selected_reviews": all_reviews,
        "ratings_answered_after_delivery": after_delivery,
        "priority_states": states,
        "reconciliation": "PASS",
    }

    output = Path("docs/delivery_analysis.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=serialize)
        + "\n",
        encoding="utf-8",
    )

    for heading, data in [
        ("DELIVERY OVERVIEW", overview),
        ("RATINGS — ALL SELECTED REVIEWS", all_reviews),
        ("RATINGS — ANSWERED AFTER DELIVERY", after_delivery),
        ("PRIORITY STATES", states),
    ]:
        print(f"\n{heading}")
        print(json.dumps(data, indent=2, ensure_ascii=False, default=serialize))

    print("\nDELIVERY RECONCILIATION: PASS")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
