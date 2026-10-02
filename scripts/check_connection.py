"""Read-only smoke test for the Neon PostgreSQL connection."""

import os
import sys

import psycopg


def main():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        print("DATABASE_URL: MISSING")
        return 1

    try:
        with psycopg.connect(
            database_url,
            connect_timeout=30,
            options=(
                "-c default_transaction_read_only=on "
                "-c statement_timeout=15000"
            ),
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT current_database(), "
                    "current_setting('server_version'), 1"
                )
                database, version, test = cursor.fetchone()

        print("NEON CONNECTION: OK")
        print(f"Database: {database}")
        print(f"PostgreSQL version: {version}")
        print(f"Query test: {test}")
        return 0

    except psycopg.Error as error:
        print("NEON CONNECTION: FAILED")
        print(f"Error type: {type(error).__name__}")
        print(f"SQLSTATE: {error.sqlstate or 'not available'}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
