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

## Phase 1 progress
- Business brief and initial KPI dictionary created.
- Main focus: sales drivers, category/state contribution, delivery and reviews.
- Customer analysis remains conditional on source profiling.
- Analytical cutoff and representative review rule remain pending.
- Phase 0 still requires quota verification and Streamlit deployment testing.

## Streamlit deployment verified
- App: https://blvckroom-ecommerce-analytics.streamlit.app/
- Entry point: dashboard/app.py.
- Public access verified by the owner in an incognito window.
- The deployment smoke test passed on 2026-10-03.
- The app currently displays project information only.
- No dataset or database credentials have been added to Streamlit.
- Remaining Phase 0 checks: service quotas and Codespaces configuration.
