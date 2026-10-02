"""Run dbt using credentials from the existing DATABASE_URL secret."""

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL: MISSING")
        return 1

    try:
        parsed = urlsplit(database_url)
        database = unquote(parsed.path.lstrip("/"))

        if (
            parsed.scheme not in {"postgres", "postgresql"}
            or not parsed.hostname
            or not parsed.username
            or not parsed.password
            or not database
        ):
            raise ValueError("Incomplete PostgreSQL URL")

        port = parsed.port or 5432
    except ValueError:
        print("DATABASE_URL: invalid connection format")
        return 1

    environment = os.environ.copy()
    environment.update({
        "DBT_ENV_SECRET_PGHOST": parsed.hostname,
        "DBT_ENV_SECRET_PGUSER": unquote(parsed.username),
        "DBT_ENV_SECRET_PGPASSWORD": unquote(parsed.password),
        "DBT_PGPORT": str(port),
        "DBT_PGDATABASE": database,
        "DBT_SEND_ANONYMOUS_USAGE_STATS": "false",
    })

    executable = Path(sys.executable).parent / "dbt"
    if not executable.is_file():
        print("dbt executable missing. Activate .venv-dbt first.")
        return 1

    arguments = sys.argv[1:]
    if not arguments:
        print("Usage: python scripts/dbt_cli.py debug")
        return 1

    result = subprocess.run(
        [
            str(executable),
            *arguments,
            "--project-dir", str(ROOT / "dbt"),
            "--profiles-dir", str(ROOT / "dbt"),
        ],
        env=environment,
        cwd=ROOT,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
