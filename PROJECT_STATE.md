# Project state

## Goal
Build a cloud-only e-commerce analytics portfolio using free services.
No Google Cloud services or paid upgrades.

## Current phase
Phase 0 — environment validation in progress.

## Verified
- Repository: https://github.com/blvckroom/ecommerce-cloud-analytics
- GitHub account has no linked payment method.
- Codespaces opens the repository on branch main.
- Python version: 3.14.2.
- Git version: 2.55.0.
- Neon project: ecommerce-cloud-analytics.
- Neon region: AWS Singapore.
- Neon plan: Free.
- Neon default branch: production.
- Database: neondb.
- PostgreSQL version observed: 18.6 (4e955f5).
- DATABASE_URL is available through Codespaces Secrets.
- Python connection and read-only SELECT test passed on 2026-10-03.

## Pending verification
- Codespaces machine type and idle timeout.
- Current Neon compute, storage and transfer quotas.
- Streamlit Community Cloud deployment smoke test.

## Next tasks
1. Commit the connection smoke test.
2. Record current free-tier limits.
3. Define the business brief and KPI dictionary.
4. Validate Streamlit deployment before completing Phase 0.

## Security
Never record passwords, tokens or connection strings here.
GitHub Actions and Streamlit secrets have not been configured.
