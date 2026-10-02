# Analytical decisions

Status: initial decisions based on source profiling.
Counts below describe the full source, not the final dashboard population.

## Commercial reporting window
Default monthly sales comparison:
2017-01-01 <= order_purchase_timestamp < 2018-08-01.

This avoids sparse early months and the uncertain ending of the dataset.
It does not prove source completeness.
August 2018 remains available for exploratory analysis with a boundary warning.
September and October 2018 are excluded from default commercial comparisons.
All source rows are retained.

## Commercial population
Use delivered orders and merchandise value from order items.
One delivered order without payment remains eligible for merchandise GMV.
Flag missing payment rather than treating it as zero.

## Review coverage
The source contains 646 delivered orders without reviews.
Exclude missing reviews from review-score denominators.
Never replace a missing review with score zero.
A deterministic representative-review rule still needs validation.

## Delivery coverage
Eight delivered orders have no actual delivery timestamp.
Keep them for sales, but exclude them from actual-delivery metrics.
Report eligible count and missing-date coverage.

## Timestamp anomalies
Observed flags:
- Carrier timestamp before purchase: 165 delivered orders.
- Delivery timestamp before carrier: 23 delivered orders.

These counts may overlap and must not be summed as distinct orders.
Retain source records and create explicit flags.
Exclude invalid timestamp pairs from duration metrics using those pairs.
Do not automatically exclude such orders from merchandise GMV or late rate.
Absence of a detected anomaly is not proof that all timestamps are accurate.

## Customer segmentation
Full-source repeat purchaser rate is approximately 3 percent.
Most customers have one delivered order.
Use Recency-Monetary segmentation plus a single/repeat purchase flag.
Do not force five Frequency quantiles or label segments as loyal without evidence.

## Retention limitations
First purchase means first observed purchase in this dataset.
Do not reset customer history at the dashboard reporting-window start.
Use earlier source history when identifying first observed purchase.
Observation cutoff and follow-up eligibility remain pending.
No-repeat purchase does not establish churn.

## Product categories
Map missing category to Unknown.
For categories lacking an English translation, retain the Portuguese name.
Do not drop products because translation is unavailable.

## Data quality tests
Require uniqueness and non-nullness for validated primary keys.
Require tested foreign-key relationships to remain valid.
Treat known missing payments, reviews and dates as documented coverage exceptions.
Reconcile order and merchandise totals before publishing marts.

## Pending checks
- Last delivered purchase date and August daily coverage.
- Review duplicate and representative-review selection rules.
- Item price, freight and payment numeric validity.
- Source version and license confirmation.
- Neon quotas and storage headroom.

## Monetary validation results
All item prices, freight values and payment values are finite,
non-missing and non-negative in this source.
Store monetary values as PostgreSQL NUMERIC, not floating point.

Retain and flag:
- 383 item rows with zero freight.
- 9 payment rows with zero payment value.

For 96,477 delivered orders with both items and payments:
- 299 have an absolute reconciliation difference above BRL 0.01.
- 246 have an absolute difference above BRL 1.00.
- Net payment minus merchandise and freight is BRL 2,831.48.

These differences are source observations, not transformation failures.
Do not overwrite payment values to force equality.
Require marts to reproduce source totals and preserve reconciliation flags.

## Representative review rule
Select one review per order by:
1. review_answer_timestamp descending, NULLS LAST.
2. review_creation_date descending, NULLS LAST.
3. review_id descending.

The current source has no ties at the highest selection rank.
review_id alone is not unique: 789 IDs occur more than once.
Preserve all source review rows and use order_id as the key of
the selected-review analytical table.

There are 202 orders with conflicting review scores.
Review selection sensitivity remains part of the statistical analysis.

## Review timing and interpretation
Of 95,824 delivered orders with comparable selected review-answer
and delivery timestamps, 4,653 reviews were answered before delivery.

Retain them in overall review reporting.
Create a review_answer_before_delivery flag.
For delivery-rating analysis, report the full eligible sample
and a sensitivity analysis restricted to answers at or after delivery.
Neither comparison establishes causality.

## Observation boundary
The last delivered-order purchase is 2018-08-29T15:00:37.
Delivered purchase counts taper strongly near the end of August.
This supports excluding August from default full-month comparisons,
but does not establish the exact source collection cutoff.

Default commercial window remains:
2017-01-01 <= order_purchase_timestamp < 2018-08-01.

For customer analysis:
- Use source purchase history before 2017 when finding first observed purchase.
- Include eligible purchases only before 2018-08-01.
- Use 2018-07-31 as the declared observation-end calendar date.
- Use 2018-08-01 as the fixed RFM/RM as-of date.
- Apply explicit 30/60/90-day follow-up eligibility.
- Preserve the distinction between first observed and lifetime first purchase.

These analyses use final snapshot order status.
They are not point-in-time reconstructions.

## Pending checks update
Review ordering, monetary validity and the analytical boundary
are now resolved for the initial model.
Source version, license, Neon quotas and storage headroom remain pending.
