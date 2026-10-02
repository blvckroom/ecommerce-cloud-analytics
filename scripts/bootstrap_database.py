"""Create database schemas and raw tables in one transaction."""

import os
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]


def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL: MISSING")
        return 1

    ddl = (ROOT / "sql/bootstrap.sql").read_text(encoding="utf-8")

    try:
        with psycopg.connect(database_url, connect_timeout=30) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL lock_timeout = '10s'")
                cursor.execute("SET LOCAL statement_timeout = '60s'")

                # bootstrap.sql contains simple DDL without embedded semicolons.
                for statement in ddl.split(";"):
                    if statement.strip():
                        cursor.execute(statement)

                cursor.execute("""
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_schema IN (
                        'raw', 'staging', 'intermediate', 'marts', 'audit'
                    )
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_schema, table_name
                """)
                tables = cursor.fetchall()

                expected = {
                    ("raw", "customers"),
                    ("raw", "orders"),
                    ("raw", "order_items"),
                    ("raw", "payments"),
                    ("raw", "reviews"),
                    ("raw", "products"),
                    ("raw", "sellers"),
                    ("raw", "category_translation"),
                    ("audit", "load_runs"),
                }

                if not expected.issubset(set(tables)):
                    raise RuntimeError("Expected tables are missing")

                cursor.execute(
                    "SELECT pg_size_pretty(pg_database_size(current_database()))"
                )
                database_size = cursor.fetchone()[0]

        # Reaching here means the transaction committed successfully.
        print("DATABASE BOOTSTRAP: OK")
        for schema, table in tables:
            print(f"  {schema}.{table}")
        print(f"Database size: {database_size}")
        print("No CSV data was loaded.")

        return 0

    except psycopg.Error as error:
        print("DATABASE BOOTSTRAP: FAILED")
        print(f"Error type: {type(error).__name__}")
        print(f"SQLSTATE: {error.sqlstate or 'not available'}")
        return 1
    except RuntimeError as error:
        print(f"DATABASE BOOTSTRAP: FAILED — {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
