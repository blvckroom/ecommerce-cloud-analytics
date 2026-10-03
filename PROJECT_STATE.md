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

## Source profiling completed
- Nine CSVs downloaded; raw files are ignored by Git.
- Source manifest includes SHA-256 checksums.
- Initial key, relationship and coverage checks completed.
- Full source contains 99,441 orders and 96,478 delivered orders.
- Analytical decisions are recorded in docs/analysis_decisions.md.
- Profiling phase remains in progress: review and numeric checks are pending.

## Analytical rules validated
- Monetary validity, review ordering and purchase boundary checks completed.
- Evidence: docs/analysis_rule_checks.json.
- Default sales comparison window: January 2017 through July 2018.
- Customer segmentation: Recency-Monetary plus repeat-purchase flag.
- Source exceptions will be retained and flagged.
- Next: confirm source metadata and Neon limits, then design database models.

## Database design preparation
- Dataset license verified: CC BY-NC-SA 4.0.
- Kaggle version number remains unverified; source checksums are recorded.
- Neon UI confirms USD 0/month and 1 GB Postgres storage.
- UI displays 100 compute hours/month; accounting details remain to be checked.
- Data transfer allowance remains unverified.
- Initial model documented in docs/data_model.md.
- No raw tables have been created or loaded yet.

## Raw ingestion verified
- Database schemas and eight raw tables created.
- Source checksums verified before loading.
- Initial load committed successfully.
- All eight raw table row counts match source profiling.
- Source monetary totals and order-status counts match PostgreSQL.
- Six tested foreign-key relationships have zero orphan rows.
- Evidence: docs/raw_validation.json.
- Database size observed: approximately 110 MB.
- Loader rerun skipped the unchanged source without duplicating rows.
- No staging or analytical models have been built yet.

## dbt staging verified
- Separate Python 3.12 environment: .venv-dbt.
- dbt Core: 1.11.15; PostgreSQL adapter: 1.11.0.
- dbt debug passed.
- Eight staging views built successfully.
- Thirty column tests and two SQL tests passed.
- Build summary: PASS=40, WARN=0, ERROR=0, SKIP=0.
- Evidence: docs/staging_build_results.json.
- Credentials are passed through environment variables.
- Raw data remains unchanged.
- Next: aggregate items and payments, select representative reviews,
  then build and reconcile order-level facts.

## Intermediate and order fact verified
- Three intermediate views built:
  int_order_item_totals, int_order_payment_totals,
  int_order_review_selected.
- Intermediate build: PASS=13, WARN=0, ERROR=0, SKIP=0.
- Order-level fct_orders view built with independent child aggregates.
- Fact build: PASS=9, WARN=0, ERROR=0, SKIP=0.
- Tests verify order count, merchandise, freight, payment totals,
  review coverage and selected coverage flags.
- Fact build evidence: docs/fct_orders_build_results.json.
- All order statuses remain available; missing values are preserved.
- No final sales KPI or business finding has been published yet.
- Next: calculate sales KPIs for the declared analytical window.

## Sales analysis verified
- Monthly sales mart build passed: 7 resources, no errors or skips.
- Monthly GMV, orders, customers and AOV reconcile independently to raw.
- Sales export and symmetric GMV decomposition completed.
- Evidence: docs/sales_results.json and docs/sales_build_results.json.
- Three initial findings documented in docs/insight_log.md.
- Next: category and customer-state contributions, prioritizing May-June 2018.

## Item and category analysis verified
- fct_order_items build passed: 16 resources, no errors or skips.
- Category monthly mart build passed: 10 resources, no errors or skips.
- Item and category merchandise totals reconcile to source and sales.
- May-June category changes reconcile exactly to -BRL 121,466.83.
- Five initial findings and one preliminary recommendation documented.
- Evidence: docs/category_changes_may_june_2018.json.
- Next: investigate category drivers and customer-state contributions.

## Category drivers analyzed
- Five priority categories decomposed into category-order volume
  and category merchandise value per order.
- All five decompositions reconcile within BRL 0.01.
- Evidence: docs/category_drivers_may_june_2018.json.
- Recommendation R01 refined by category.
- Next: customer-state contribution analysis, then delivery and reviews.

## Regional analysis verified
- State monthly mart build passed: 12 resources, no errors or skips.
- State metrics reconcile to raw and monthly sales.
- Regional export reconciliation passed.
- Evidence: docs/state_analysis.json and docs/state_build_results.json.
- SP and RJ prioritized for sales investigation.
- RJ prioritized for delivery investigation; SP has high absolute late volume.
- Recommendation R02 documented with delivery-promise guardrail.
- Next: delivery duration, delay severity and review analysis.

## Delivery analysis completed

- mart_delivery_orders selected build: PASS=12, WARN=0, ERROR=0, SKIP=0.
- Export: docs/delivery_analysis.json; reconciliation PASS.
- Analysis window: 89,860 delivered orders; 89,852 date-eligible;
  6,138 late orders; late rate 6.83%.
- Documented delivery/rating association and review-timing sensitivity.
- Recorded regional operational priorities and interpretation limits.

## Customer retention analysis completed

- int_customer_monthly selected build: PASS=3, no warnings or errors.
- mart_customer_cohort selected build: PASS=3, no warnings or errors.
- Both models reconciled independently against raw source data.
- Export: docs/customer_retention.json; reconciliation PASS.
- In-window customers: 86,960; repeat customers: 2,609 (3.00%).
- Cohort output covers M0-M12 and preserves unobserved months as NULL.
- Documented observation-window limits and repeat-purchase recommendation.
