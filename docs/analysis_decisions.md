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
