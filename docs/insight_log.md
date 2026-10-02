# Insight log

## Scope and evidence
Population: delivered orders.
Purchase window: 2017-01-01 inclusive to 2018-08-01 exclusive.
Currency: BRL.
Merchandise GMV excludes freight and is not platform net revenue.

Evidence:
- dbt model: mart_sales_monthly.
- Independent raw reconciliation test: mart_sales_monthly_reconciliation.
- Export script: scripts/export_sales.py.
- Results: docs/sales_results.json.

## Sales overview
- Merchandise GMV: BRL 12,342,450.49.
- Delivered orders: 89,860.
- Distinct purchasing customers: 86,960.
- Overall AOV: approximately BRL 137.35.

## S01 November 2017 growth was driven by order volume
GMV increased 52.37 percent from October.
Delivered orders increased from 4,478 to 7,289, approximately 62.77 percent.
AOV declined approximately 6.39 percent.

Symmetric decomposition:
- Order-volume contribution: +BRL 393,929.73.
- AOV contribution: -BRL 54,412.01.
- Net GMV change: +BRL 339,517.72.

This identifies arithmetic drivers, not the cause of the order increase.
Investigate category and region contributions before attributing the change
to campaigns, pricing or external events.

## S02 AOV offset declining order volume in April and May 2018
Delivered orders fell from 7,003 in March to 6,798 in April
and 6,749 in May.

GMV nevertheless rose 2.12 percent in April and 0.41 percent in May.
Positive AOV contributions exceeded negative order-volume contributions.

Investigate whether category mix or within-category order values changed.
Do not conclude that pricing improved without item-level evidence.

## S03 June 2018 decline was mainly associated with lower order volume
GMV fell 12.43 percent from May, a decrease of BRL 121,466.83.

Symmetric decomposition:
- Order-volume contribution: -BRL 92,692.12.
- AOV contribution: -BRL 28,774.71.
- Order volume accounted for approximately 76.31 percent of the net decline.

July GMV increased 1.39 percent from June but remained below May.
Prioritize category and regional contribution analysis for May to June.
Do not infer customer churn or a causal operational problem from this result.

## Method limitations
The decomposition is an arithmetic attribution of GMV = orders * AOV.
Order statuses reflect the final historical snapshot.
Monthly customer counts cannot be summed to obtain full-period customers.
These findings do not demonstrate business impact from an intervention.
