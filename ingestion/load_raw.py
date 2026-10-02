"""Validate and load the initial Olist source into Neon atomically."""

import csv
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/olist"

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


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def table_count(cursor, table):
    cursor.execute(
        sql.SQL("SELECT COUNT(*) FROM {}").format(
            sql.Identifier("raw", table)
        )
    )
    return cursor.fetchone()[0]


def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL: MISSING")
        return 1

    manifest_path = ROOT / "data/source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profile = json.loads(
        (ROOT / "docs/source_profile.json").read_text(encoding="utf-8")
    )
    manifest_hash = sha256(manifest_path)
    source_files = {entry["name"]: entry for entry in manifest["files"]}

    # Validate sources before opening a database connection.
    for table, filename in TABLES.items():
        path = SOURCE / filename
        if sha256(path) != source_files[filename]["sha256"]:
            raise ValueError(f"Source checksum mismatch: {filename}")
        if profile[filename]["rows"] <= 0:
            raise ValueError(f"Unexpected empty source: {filename}")

    print("SOURCE CHECKSUMS: OK", flush=True)
    run_id = uuid.uuid4()
    started = False

    with psycopg.connect(database_url, connect_timeout=30) as connection:
        try:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO audit.load_runs
                            (run_id, status, source_manifest_sha256)
                        VALUES (%s, 'running', %s)
                        """,
                        (run_id, manifest_hash),
                    )
            started = True

            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute("SET LOCAL lock_timeout = '15s'")
                    cursor.execute("SET LOCAL statement_timeout = '300s'")

                    # Prevent two cooperating loaders from running together.
                    cursor.execute(
                        "SELECT pg_try_advisory_xact_lock(730021)"
                    )
                    if not cursor.fetchone()[0]:
                        raise ValueError("Another loader is running")

                    counts = {
                        table: table_count(cursor, table)
                        for table in TABLES
                    }

                    if any(counts.values()):
                        cursor.execute(
                            """
                            SELECT EXISTS (
                                SELECT 1 FROM audit.load_runs
                                WHERE status = 'success'
                                  AND source_manifest_sha256 = %s
                            )
                            """,
                            (manifest_hash,),
                        )
                        previous_success = cursor.fetchone()[0]

                        counts_match = all(
                            counts[table] == profile[filename]["rows"]
                            for table, filename in TABLES.items()
                        )

                        if not previous_success or not counts_match:
                            raise ValueError(
                                "Raw data already exists without a matching "
                                "successful load; refusing to overwrite"
                            )

                        cursor.execute(
                            """
                            UPDATE audit.load_runs
                            SET status = 'skipped',
                                finished_at = CURRENT_TIMESTAMP,
                                details = %s
                            WHERE run_id = %s
                            """,
                            (
                                Jsonb({
                                    "reason": "same manifest and matching counts",
                                    "rows": counts,
                                }),
                                run_id,
                            ),
                        )
                        print(
                            "LOAD: SKIPPED — same source already loaded",
                            flush=True,
                        )

                    else:
                        loaded = {}

                        for table, filename in TABLES.items():
                            cursor.execute(
                                """
                                SELECT column_name
                                FROM information_schema.columns
                                WHERE table_schema = 'raw'
                                  AND table_name = %s
                                ORDER BY ordinal_position
                                """,
                                (table,),
                            )
                            columns = [
                                row[0] for row in cursor.fetchall()
                            ]
                            if not columns:
                                raise ValueError(f"Missing raw table: {table}")

                            temp_table = f"load_{table}"
                            cursor.execute(
                                sql.SQL(
                                    "CREATE TEMP TABLE {} "
                                    "(LIKE {} INCLUDING ALL) ON COMMIT DROP"
                                ).format(
                                    sql.Identifier(temp_table),
                                    sql.Identifier("raw", table),
                                )
                            )

                            copy_statement = sql.SQL(
                                "COPY {} ({}) FROM STDIN"
                            ).format(
                                sql.Identifier(temp_table),
                                sql.SQL(", ").join(
                                    sql.Identifier(column)
                                    for column in columns
                                ),
                            )

                            with (SOURCE / filename).open(
                                encoding="utf-8-sig", newline=""
                            ) as stream:
                                reader = csv.DictReader(stream)
                                expected_header = profile[filename]["columns"]
                                if reader.fieldnames != expected_header:
                                    raise ValueError(
                                        f"Header mismatch: {filename}"
                                    )

                                missing_columns = (
                                    set(columns)
                                    - set(reader.fieldnames)
                                    - {"source_row_number"}
                                )
                                if missing_columns:
                                    raise ValueError(
                                        f"Missing columns: {filename}"
                                    )

                                with cursor.copy(copy_statement) as copy:
                                    for number, row in enumerate(reader, 1):
                                        if (
                                            None in row
                                            or any(
                                                value is None
                                                for value in row.values()
                                            )
                                        ):
                                            raise ValueError(
                                                f"Malformed record: {filename}"
                                            )

                                        values = [
                                            number
                                            if column == "source_row_number"
                                            else (
                                                None
                                                if row[column] == ""
                                                else row[column]
                                            )
                                            for column in columns
                                        ]
                                        copy.write_row(values)

                            cursor.execute(
                                sql.SQL("SELECT COUNT(*) FROM {}").format(
                                    sql.Identifier(temp_table)
                                )
                            )
                            count = cursor.fetchone()[0]
                            if count != profile[filename]["rows"]:
                                raise ValueError(
                                    f"Row count mismatch: {filename}"
                                )

                            loaded[table] = count
                            print(
                                f"Validated {table}: {count:,} rows",
                                flush=True,
                            )

                        # Publish all tables only after all sources validate.
                        for table in TABLES:
                            cursor.execute(
                                sql.SQL(
                                    "INSERT INTO {} SELECT * FROM {}"
                                ).format(
                                    sql.Identifier("raw", table),
                                    sql.Identifier(f"load_{table}"),
                                )
                            )
                            if table_count(cursor, table) != loaded[table]:
                                raise ValueError(
                                    f"Published row count mismatch: {table}"
                                )

                        cursor.execute(
                            """
                            SELECT pg_database_size(current_database())
                            """
                        )
                        size_bytes = cursor.fetchone()[0]
                        if size_bytes > 350 * 1024 * 1024:
                            raise ValueError(
                                "Database exceeds internal 350 MiB target"
                            )

                        cursor.execute(
                            """
                            UPDATE audit.load_runs
                            SET status = 'success',
                                finished_at = CURRENT_TIMESTAMP,
                                details = %s
                            WHERE run_id = %s
                            """,
                            (
                                Jsonb({
                                    "rows": loaded,
                                    "database_bytes_before_commit": size_bytes,
                                }),
                                run_id,
                            ),
                        )

            print("LOAD TRANSACTION: COMMITTED", flush=True)

            with connection.transaction():
                with connection.cursor() as cursor:
                    for table in TABLES:
                        print(
                            f"raw.{table}: "
                            f"{table_count(cursor, table):,} rows"
                        )
                    cursor.execute(
                        "SELECT pg_size_pretty("
                        "pg_database_size(current_database()))"
                    )
                    print(f"Database size: {cursor.fetchone()[0]}")

            return 0

        except Exception as error:
            if started:
                try:
                    with connection.transaction():
                        with connection.cursor() as cursor:
                            cursor.execute(
                                """
                                UPDATE audit.load_runs
                                SET status = 'failed',
                                    finished_at = CURRENT_TIMESTAMP,
                                    details = %s
                                WHERE run_id = %s AND status = 'running'
                                """,
                                (
                                    Jsonb({
                                        "error_type": type(error).__name__,
                                    }),
                                    run_id,
                                ),
                            )
                except psycopg.Error:
                    print("Could not finalize audit failure status")

            print("LOAD: FAILED")
            print(f"Error type: {type(error).__name__}")
            if isinstance(error, psycopg.Error):
                print(f"SQLSTATE: {error.sqlstate or 'not available'}")
            elif isinstance(error, ValueError):
                print(str(error))
            return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"LOAD: FAILED — {type(error).__name__}")
        if isinstance(error, ValueError):
            print(str(error))
        sys.exit(1)
