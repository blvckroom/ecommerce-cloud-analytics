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

## S04 Five categories account for 51.68 percent of gross GMV decline
Comparison: May to June 2018, delivered orders.

- Gross decline across 41 declining categories: BRL 175,462.79.
- Gross increase across 26 increasing categories: BRL 53,995.96.
- Net change: -BRL 121,466.83, reconciled to the sales mart.
- The five largest declining categories account for 51.68 percent
  of gross decline.

Largest declines:
1. watches_gifts: -BRL 34,337.41.
2. garden_tools: -BRL 19,752.07.
3. sports_leisure: -BRL 14,293.91.
4. furniture_decor: -BRL 11,664.23.
5. cool_stuff: -BRL 10,632.75.

Prioritize these categories for further investigation.
This concentration does not identify the cause of the decline.

## S05 Category movements are mixed, not uniformly negative
health_beauty increased BRL 12,211.34, or 12.92 percent,
offsetting part of the declines elsewhere.

signaling_and_security increased 757.82 percent but from a May base
of only BRL 683.50, producing an absolute increase of BRL 5,179.68.
Use absolute GMV contributions alongside growth percentages
when prioritizing categories.

Evidence:
- scripts/export_category_changes.py.
- docs/category_changes_may_june_2018.json.
- mart_category_monthly and its raw reconciliation tests.

## Preliminary recommendation R01
Investigate watches_gifts and garden_tools first, followed by the
remaining three largest declining categories.

Check category order count, category merchandise value per order,
item count, average item price and product/seller concentration.
These checks help distinguish arithmetic drivers; they do not
establish demand, price-change or inventory causes by themselves.

Track recovered category GMV and order volume in any future pilot.
Review delivery performance and rating as guardrails.
No intervention or measured business improvement has occurred.

## S06 Category declines require different investigations
Comparison: May to June 2018, delivered orders.

watches_gifts:
- Category orders fell from 585 to 444.
- Category merchandise value per order fell from BRL 204.04 to 191.50.
- Order-volume effect: -BRL 27,886.01.
- Category-value effect: -BRL 6,451.40.

garden_tools:
- Category orders fell from 227 to 148.
- Category merchandise value per order fell from BRL 166.08 to 121.28.
- Order-volume effect: -BRL 11,350.64.
- Category-value effect: -BRL 8,401.43.
- Average item price fell from BRL 130.91 to 97.55.
- Product mix must be checked before inferring price changes.

sports_leisure:
- Both category orders and category merchandise value per order declined.

furniture_decor and cool_stuff:
- Category orders declined while category merchandise value per order rose.
- Higher value per order partially offset the order-volume decline.
- These results do not justify an immediate discount recommendation.

Category merchandise value per order is not total-basket AOV.
Orders can contain multiple categories.
The decomposition is arithmetic, not causal.

Evidence:
- scripts/export_category_drivers.py.
- docs/category_drivers_may_june_2018.json.

## Recommendation R01 refinement
Prioritize order-volume investigation for watches_gifts,
furniture_decor and cool_stuff.

For garden_tools and sports_leisure, investigate both order volume
and product mix/value per category order.

Compare product and seller contributions before suggesting pricing,
inventory or marketing interventions. Relevant operational and
commercial data would be required to establish those causes.
