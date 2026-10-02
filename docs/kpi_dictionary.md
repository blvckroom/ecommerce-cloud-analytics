# KPI dictionary

Status: initial definitions.
Source coverage and analytical cutoff must be verified during profiling.

## Shared rules
- Currency: BRL.
- Commercial population: orders with order_status = 'delivered'.
- Commercial reporting date: order_purchase_timestamp.
- Delivered status is taken from the final historical dataset snapshot.
- Do not describe these metrics as real-time or point-in-time reporting.
- Customer identity across orders: customer_unique_id.
- customer_id is used to join orders to the customers source table.
- A zero denominator returns NULL, not zero.
- Incomplete boundary months must be identified before growth analysis.

## Delivered merchandise GMV
Sum of order-item price for delivered orders.
Exclude freight_value.
This is merchandise value, not Olist platform net revenue.

## Delivered orders
Count distinct order_id in the commercial population.

## Average order value
Delivered merchandise GMV divided by delivered orders.
Do not calculate AOV as the average price of an item.

## Purchasing customers
Count distinct customer_unique_id in the commercial population.
Counts across periods are not additive.

## Monthly GMV growth
(Current month GMV / previous month GMV - 1) * 100.
Return NULL when the previous month is missing or zero.
Flag incomplete months rather than presenting them as comparable months.

## Category contribution
Category GMV divided by total GMV in the same selected population.
Retain missing categories as Unknown to preserve reconciliation.

## Repeat purchaser rate
Customers with at least two delivered orders divided by customers
with at least one delivered order in the observation window.
This is an observed repeat-purchase measure, not a churn rate.

## Late delivery rate
Delivered orders whose actual delivery calendar date is later than
their estimated delivery calendar date, divided by delivered orders
with both dates available.
Missing delivery dates are excluded from this denominator.
Report eligible order count and date coverage separately.

## Delivery time
Actual delivery timestamp minus purchase timestamp, expressed in days.
Report median and p90.
Flag negative durations for investigation.

## Review score
Use one representative valid review per order.
The selection rule must be finalized after profiling review multiplicity.
Report mean, distribution, sample size and review coverage.

## Low rating rate
Orders with a representative review score of 1 or 2 divided by orders
with a valid representative review.
Missing reviews are not scored as zero.

## Repeat purchase within 30, 60 or 90 days
Customers with another delivered purchase within the stated window
after their first delivered purchase, divided by customers with
sufficient observation time for that window.
The observation cutoff must be documented.
Insufficient follow-up is excluded, not treated as no repeat purchase.

## Monthly cohort retention
Customers purchasing in month offset k divided by customers in the
cohort defined by their first delivered purchase month.
M0 is 100 percent.
Unobserved future months are NULL, not zero.

## RFM or alternative segmentation
Recency: days from last delivered purchase to a fixed analysis date.
Frequency: count distinct delivered orders.
Monetary: delivered merchandise GMV per customer.
Do not use today's date for this historical dataset.
Use RFM only if frequency provides meaningful differentiation.
Otherwise consider Recency-Monetary with a repeat-purchase flag.

## Join safety
Aggregate order items, payments and reviews independently to order grain
before combining them in an order-level analytical table.
Joining all three detail tables directly can multiply rows and amounts.

## Filter consistency
Each dashboard metric must document its population and filter behavior.
Customer counts and AOV must be recomputed for the selected population.
Cohort filters must not silently change the original cohort denominator.
