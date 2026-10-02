# Data model

## Schemas
- raw: selected source columns, preserving source records.
- staging: typed and standardized source views.
- intermediate: reusable aggregation and review-selection views.
- marts: analytical facts, dimensions and dashboard outputs.
- audit: load history and source validation evidence.

## Raw tables
| Table | Grain |
|---|---|
| raw.customers | customer_id |
| raw.orders | order_id |
| raw.order_items | order_id and order_item_id |
| raw.payments | order_id and payment_sequential |
| raw.reviews | one source CSV record |
| raw.products | product_id |
| raw.sellers | seller_id |
| raw.category_translation | product_category_name |

Geolocation is excluded from the initial database.
Review text is excluded; score, IDs and timestamps are retained.
Record review source row numbers for traceability.
Do not enforce uniqueness on review_id alone.

Retain every source order status and purchase date.
Apply analytical filters downstream rather than deleting raw history.

## Intermediate models
- int_order_item_totals: one row per order_id.
- int_order_payment_totals: one row per order_id.
- int_order_review_selected: one row per order_id.

Review selection:
answer timestamp DESC NULLS LAST,
creation timestamp DESC NULLS LAST,
review_id DESC.

Aggregate each child independently before joining to orders.

## Analytical facts
### fct_orders
Grain: one row per order_id.

Contains:
- Order and customer identifiers.
- customer_unique_id for cross-order customer analysis.
- Customer state from the order-associated source customer record.
- Status and order timestamps.
- Merchandise value, freight value and payment value.
- Item count and payment-record count.
- Representative review score and timestamps.
- Coverage, reconciliation and timestamp-anomaly flags.

Use LEFT JOIN from orders to aggregated child tables.
A missing payment is NULL with a flag, not automatically zero.

### fct_order_items
Grain: order_id and order_item_id.

Contains product_id, seller_id, item price and freight.
Use this fact for category and seller analysis.
Do not assign a single product or seller to a multi-item order.

## Dimensions
- dim_customer: one row per customer_unique_id.
- dim_product: one row per product_id.
- dim_seller: one row per seller_id.
- dim_date: one row per calendar date.

Customer location at an order belongs in the order fact.
Do not assume each customer has one permanent state across all orders.

Missing product category becomes Unknown.
Untranslated categories retain their original source labels.

## Initial dashboard outputs
- mart_sales_monthly: one row per purchase month.
- mart_category_monthly: one row per month and category.
- mart_state_monthly: one row per month and customer state.
- mart_delivery_orders: one row per eligible delivered order.
- mart_customer_summary: one row per customer and fixed as-of date.
- mart_customer_retention: cohort and observation window or month offset.

Different marts may use different eligible populations.
Document their denominators and do not join aggregate marts
in a way that multiplies totals.

## Materialization
Staging and intermediate models default to views.
Choose fact and mart materialization after measuring query performance
and storage requirements. Avoid unnecessary copies of the same data.

## Analysis rules
Default sales window:
2017-01-01 <= purchase timestamp < 2018-08-01.

Use earlier source history for first observed customer purchase.
Customer observation end: 2018-07-31.
Fixed customer segmentation as-of date: 2018-08-01.
Statuses reflect the final source snapshot, not point-in-time knowledge.

## Required checks
- Unique and non-null validated keys.
- Valid foreign-key relationships.
- No order-level fanout.
- Source-to-model row and money reconciliation.
- Explicit handling of known coverage exceptions.
- Database size measured after loading and transformation.
