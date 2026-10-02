"""Profile source CSVs without modifying them or connecting to Neon."""

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/olist"
DOCS = ROOT / "docs"

KEYS = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_order_items_dataset.csv": ["order_id", "order_item_id"],
    "olist_order_payments_dataset.csv": ["order_id", "payment_sequential"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "product_category_name_translation.csv": ["product_category_name"],
}

DETAIL_FILES = {
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
}

DATE_COLUMNS = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def profile(path):
    rows = 0
    missing = Counter()
    keys_seen = set()
    duplicate_keys = 0
    missing_keys = 0
    orders = Counter()
    statuses = Counter()
    scores = Counter()
    dates = {
        column: {"min": None, "max": None, "invalid": 0}
        for column in DATE_COLUMNS.get(path.name, [])
    }

    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames

        if not columns:
            raise ValueError(f"No CSV header: {path.name}")

        for row in reader:
            rows += 1

            # DictReader uses None for extra fields or missing trailing fields.
            if None in row or any(value is None for value in row.values()):
                raise ValueError(
                    f"Malformed CSV record: {path.name}, record {rows}"
                )

            for column, value in row.items():
                if not value.strip():
                    missing[column] += 1

            key_columns = KEYS.get(path.name)
            if key_columns:
                key = tuple(row[column].strip() for column in key_columns)
                if any(not value for value in key):
                    missing_keys += 1
                else:
                    if key in keys_seen:
                        duplicate_keys += 1
                    keys_seen.add(key)

            if path.name in DETAIL_FILES:
                order_id = row["order_id"].strip()
                if order_id:
                    orders[order_id] += 1

            if path.name == "olist_orders_dataset.csv":
                statuses[row["order_status"]] += 1

            if path.name == "olist_order_reviews_dataset.csv":
                scores[row["review_score"]] += 1

            for column, summary in dates.items():
                value = row[column].strip()
                if not value:
                    continue
                try:
                    parsed = datetime.fromisoformat(value).isoformat()
                except ValueError:
                    summary["invalid"] += 1
                    continue
                if summary["min"] is None or parsed < summary["min"]:
                    summary["min"] = parsed
                if summary["max"] is None or parsed > summary["max"]:
                    summary["max"] = parsed

    result = {
        "rows": rows,
        "columns": columns,
        "missing_cells": {
            column: missing[column] for column in columns
        },
        "candidate_key": KEYS.get(path.name),
        "missing_key_rows": missing_keys if path.name in KEYS else None,
        "duplicate_key_rows": duplicate_keys if path.name in KEYS else None,
    }

    if orders:
        result["order_multiplicity"] = {
            "distinct_orders": len(orders),
            "orders_with_multiple_rows": sum(
                count > 1 for count in orders.values()
            ),
            "max_rows_per_order": max(orders.values()),
        }

    if statuses:
        result["order_status_counts"] = dict(statuses)
    if scores:
        result["review_score_counts"] = dict(scores)
    if dates:
        result["date_ranges"] = dates

    return result


def main():
    files = sorted(SOURCE.glob("*.csv"))
    if len(files) != 9:
        raise ValueError(f"Expected 9 source CSVs, found {len(files)}")

    DOCS.mkdir(exist_ok=True)

    manifest = {
        "dataset": "olistbr/brazilian-ecommerce",
        "source_url": (
            "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
        ),
        "manifest_created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_version": "pending verification",
        "license": "pending verification on source data card",
        "files": [],
    }

    report = {}
    lines = [
        "# Initial source quality report",
        "",
        "Generated from source CSVs without modifying them.",
        "Geolocation is checksummed but excluded from MVP profiling.",
        "Candidate keys require further relationship validation.",
        "",
    ]

    for path in files:
        manifest["files"].append({
            "name": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": checksum(path),
        })

        if path.name == "olist_geolocation_dataset.csv":
            print(f"{path.name}: checksum recorded; profiling skipped")
            continue

        result = profile(path)
        report[path.name] = result

        print(f"\n{path.name}")
        print(f"  Rows: {result['rows']:,}")

        if result["candidate_key"]:
            print(f"  Missing key rows: {result['missing_key_rows']}")
            print(f"  Duplicate key rows: {result['duplicate_key_rows']}")

        if "order_multiplicity" in result:
            print(f"  Order multiplicity: {result['order_multiplicity']}")
        if "order_status_counts" in result:
            print(f"  Statuses: {result['order_status_counts']}")
        if "review_score_counts" in result:
            print(f"  Scores: {result['review_score_counts']}")
        if "date_ranges" in result:
            print(f"  Date ranges: {result['date_ranges']}")

        lines.extend([
            f"## {path.name}",
            "",
            "```json",
            json.dumps(result, ensure_ascii=False, indent=2),
            "```",
            "",
        ])

    (ROOT / "data/source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (DOCS / "source_profile.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (DOCS / "data_quality_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print("\nPROFILE: COMPLETE")
    print("Created data/source_manifest.json")
    print("Created docs/source_profile.json")
    print("Created docs/data_quality_report.md")


if __name__ == "__main__":
    main()
