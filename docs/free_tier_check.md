# Free tier verification

Verification date: 2026-10-03.
Evidence: account information reported by the project owner and Neon UI.

## GitHub
- Personal account has no linked payment method.
- Codespaces is operational.
- Usage was initially blank.
- Public repository: blvckroom/ecommerce-cloud-analytics.
- Codespaces configuration was acknowledged by the owner.
- Remaining usage should be monitored during development.

## Neon
- Current plan: Free, USD 0 per month.
- Region: AWS Singapore.
- Postgres allowance displayed: 100 compute hours per month.
- Postgres storage allowance displayed: 1 GB.
- Maximum autoscaling displayed: 2 CU.
- Scale to zero when idle is available.
- Compute accounting details must be checked when interpreting usage.
- Data transfer allowance remains unverified.

Functions and object storage are not used by this project.
The displayed 5 GB object storage allowance is not a transfer allowance.

## Streamlit
- Public app deployment passed.
- Incognito access was verified by the owner.
- No database secret has been configured for the app.

## Internal operating targets
- Target steady-state database size below 350 MB.
- Measure actual database and relation sizes after loading.
- Preserve space for indexes and transformations.
- Exclude geolocation and review text from the initial database load.
- Use views for staging and intermediate models where practical.
- No paid upgrade or trial dependency is authorized.
