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

## S07 SP and RJ account for the largest May-June regional declines
Delivered merchandise GMV changes:
- SP: -BRL 84,031.42.
- RJ: -BRL 23,978.21.
- Combined: -BRL 108,009.63.
- Total net change across all states: -BRL 121,466.83.

Other states include both declines and increases.
Prioritize SP and RJ for commercial investigation.
Category and state decompositions overlap and must not be added together.

## S08 RJ combines substantial GMV exposure with elevated delivery lateness
Window: January 2017 through July 2018, delivered orders.

Overall:
- Eligible orders: 89,852.
- Late orders: 6,138.
- Late delivery rate: approximately 6.83 percent.

RJ:
- Merchandise GMV: BRL 1,657,663.30.
- Eligible orders: 11,587.
- Late orders: 1,453.
- Late delivery rate: approximately 12.54 percent.

SP:
- Eligible orders: 37,235.
- Late orders: 1,532.
- Late delivery rate: approximately 4.11 percent.

RJ has nearly as many late orders as SP despite a much smaller order volume.
SP and RJ together account for 2,985 of the 6,138 late orders.

State comparisons are descriptive and may reflect differences in
seller mix, geography, categories, delivery promises and time periods.
Full-window lateness does not explain the May-June sales decline by itself.

## Recommendation R02
Prioritize an operational investigation of RJ, while also reviewing
SP because of its large absolute number of late orders.

Break down delivery performance by month, seller and category.
Measure actual delivery duration, delay severity and review outcomes.
Review whether promised delivery dates are realistic.
Do not improve the late-rate KPI simply by extending delivery promises.

Pilot evaluation should track:
- Late delivery rate and affected order count.
- Median and p90 delivery duration.
- Review score and low-rating rate.
- Length of promised delivery time as a guardrail.

No operational intervention or improvement has been measured.

Evidence:
- scripts/export_state_analysis.py.
- docs/state_analysis.json.
- mart_state_monthly and its reconciliation tests.

## S09 — Delivery timeliness and customer ratings

Scope: delivered orders purchased from 2017-01-01 inclusive to
2018-08-01 exclusive. Source: docs/delivery_analysis.json.

Of 89,860 delivered orders, 89,852 had sufficient dates to classify
timeliness. There were 6,138 late orders (6.83%). Eight orders were
excluded from the timeliness denominator because of missing dates.

Median delivery duration was 10.62 days; P90 was 23.61 days.
Among late orders, median calendar days late was 7 and P90 was 23.

Among orders with a selected review, late orders had an average
score of 2.22 versus 4.28 for on-time orders. The share of scores
1–2 was 63.69% versus 9.38%, a gap of 54.31 percentage points.

This is an observed association, not a causal estimate.
Ratings may also reflect product, seller, service and other factors.

## S10 — Review timing materially changes the comparison

Restricting selected reviews to answer timestamps at or after actual
delivery reduced the reviewed late-order sample from 5,993 to 1,702.

In this subset, low-rating shares were 20.09% for late orders and
9.36% for on-time orders, a gap of 10.73 percentage points.
Average scores were 3.69 and 4.28 respectively.

The association remained, but its magnitude changed substantially.
This restriction changes sample composition and must not be treated
as an unbiased replacement for the full reviewed population.
Answer timestamp does not establish when the review was first created.

## R03 — Investigate late delivery with review-timing safeguards

Prioritize RJ for its 12.54% late rate and median delay of 10 calendar
days. Also investigate SP, which had 1,532 late orders compared with
1,453 in RJ despite a lower late rate of 4.11%.

Segment patterns by purchase month, seller and product category
before assigning operational causes. Present both full-sample and
review-timing sensitivity results.

Monitor actual delivery duration and days late alongside promised
delivery duration. Extending delivery promises alone should not
be interpreted as improved fulfillment.

Do not infer that late delivery caused the May–June GMV decline
from these descriptive results.

## S11 — Repeat purchasing within the analysis window

Source: docs/customer_retention.json.
Window: delivered purchases from 2017-01-01 inclusive to
2018-08-01 exclusive. Customer identity: customer_unique_id.

There were 86,960 purchasing customers and 89,860 delivered orders.
Of these customers, 84,351 placed one order within the window and
2,609 placed at least two orders. The repeat customer rate was 3.00%.

This is a window-specific purchase frequency measure, not a churn
rate. Customers entering near the end of the window had less time
to make another purchase. Multiple purchases within one month count
toward repeat purchasing but do not imply next-month retention.

## S12 — Monthly cohort retention

Cohorts use first observed delivered purchase month, including
available 2016 history. Retention measures activity in a specific
month after cohort entry; it is not cumulative return probability.

For cohorts starting from January 2017 with sufficient observation:
- M1: 389 / 81,001 customers = 0.4802%.
- M3: 180 / 68,617 customers = 0.2623%.
- M6: 115 / 48,973 customers = 0.2348%.
- M12: 31 / 17,344 customers = 0.1787%.

Eligible cohort composition changes across horizons. These pooled
values must not be interpreted as a single fixed population's
retention trajectory.

The 2017-onward cohort population contains 86,950 customers.
Ten additional customers purchasing within the analysis window
had their first observed delivered purchase in 2016.

Unobserved months remain NULL rather than zero. First observed
purchase does not necessarily equal first lifetime purchase.

## R04 — Design and evaluate repeat-purchase experiments

Investigate repeat purchasing by first-purchase category, acquisition
cohort and delivery experience before selecting target segments.

Consider a post-purchase communication or relevant product
recommendation experiment. Evaluate a predefined repeat-purchase
window, such as 90 days, using customers with sufficient follow-up
and a randomized control group.

Use incremental repeat purchasing as an outcome and monitor
communication opt-outs and incentive cost. Profitability evaluation
requires additional cost and margin data unavailable in this dataset.

Do not claim that a CRM intervention has already been validated.
