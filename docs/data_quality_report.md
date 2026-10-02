# Initial source quality report

Generated from source CSVs without modifying them.
Geolocation is checksummed but excluded from MVP profiling.
Candidate keys require further relationship validation.

## olist_customers_dataset.csv

```json
{
  "rows": 99441,
  "columns": [
    "customer_id",
    "customer_unique_id",
    "customer_zip_code_prefix",
    "customer_city",
    "customer_state"
  ],
  "missing_cells": {
    "customer_id": 0,
    "customer_unique_id": 0,
    "customer_zip_code_prefix": 0,
    "customer_city": 0,
    "customer_state": 0
  },
  "candidate_key": [
    "customer_id"
  ],
  "missing_key_rows": 0,
  "duplicate_key_rows": 0
}
```

## olist_order_items_dataset.csv

```json
{
  "rows": 112650,
  "columns": [
    "order_id",
    "order_item_id",
    "product_id",
    "seller_id",
    "shipping_limit_date",
    "price",
    "freight_value"
  ],
  "missing_cells": {
    "order_id": 0,
    "order_item_id": 0,
    "product_id": 0,
    "seller_id": 0,
    "shipping_limit_date": 0,
    "price": 0,
    "freight_value": 0
  },
  "candidate_key": [
    "order_id",
    "order_item_id"
  ],
  "missing_key_rows": 0,
  "duplicate_key_rows": 0,
  "order_multiplicity": {
    "distinct_orders": 98666,
    "orders_with_multiple_rows": 9803,
    "max_rows_per_order": 21
  }
}
```

## olist_order_payments_dataset.csv

```json
{
  "rows": 103886,
  "columns": [
    "order_id",
    "payment_sequential",
    "payment_type",
    "payment_installments",
    "payment_value"
  ],
  "missing_cells": {
    "order_id": 0,
    "payment_sequential": 0,
    "payment_type": 0,
    "payment_installments": 0,
    "payment_value": 0
  },
  "candidate_key": [
    "order_id",
    "payment_sequential"
  ],
  "missing_key_rows": 0,
  "duplicate_key_rows": 0,
  "order_multiplicity": {
    "distinct_orders": 99440,
    "orders_with_multiple_rows": 2961,
    "max_rows_per_order": 29
  }
}
```

## olist_order_reviews_dataset.csv

```json
{
  "rows": 99224,
  "columns": [
    "review_id",
    "order_id",
    "review_score",
    "review_comment_title",
    "review_comment_message",
    "review_creation_date",
    "review_answer_timestamp"
  ],
  "missing_cells": {
    "review_id": 0,
    "order_id": 0,
    "review_score": 0,
    "review_comment_title": 87658,
    "review_comment_message": 58274,
    "review_creation_date": 0,
    "review_answer_timestamp": 0
  },
  "candidate_key": null,
  "missing_key_rows": null,
  "duplicate_key_rows": null,
  "order_multiplicity": {
    "distinct_orders": 98673,
    "orders_with_multiple_rows": 547,
    "max_rows_per_order": 3
  },
  "review_score_counts": {
    "4": 19142,
    "5": 57328,
    "1": 11424,
    "3": 8179,
    "2": 3151
  },
  "date_ranges": {
    "review_creation_date": {
      "min": "2016-10-02T00:00:00",
      "max": "2018-08-31T00:00:00",
      "invalid": 0
    },
    "review_answer_timestamp": {
      "min": "2016-10-07T18:32:28",
      "max": "2018-10-29T12:27:35",
      "invalid": 0
    }
  }
}
```

## olist_orders_dataset.csv

```json
{
  "rows": 99441,
  "columns": [
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
  ],
  "missing_cells": {
    "order_id": 0,
    "customer_id": 0,
    "order_status": 0,
    "order_purchase_timestamp": 0,
    "order_approved_at": 160,
    "order_delivered_carrier_date": 1783,
    "order_delivered_customer_date": 2965,
    "order_estimated_delivery_date": 0
  },
  "candidate_key": [
    "order_id"
  ],
  "missing_key_rows": 0,
  "duplicate_key_rows": 0,
  "order_status_counts": {
    "delivered": 96478,
    "invoiced": 314,
    "shipped": 1107,
    "processing": 301,
    "unavailable": 609,
    "canceled": 625,
    "created": 5,
    "approved": 2
  },
  "date_ranges": {
    "order_purchase_timestamp": {
      "min": "2016-09-04T21:15:19",
      "max": "2018-10-17T17:30:18",
      "invalid": 0
    },
    "order_approved_at": {
      "min": "2016-09-15T12:16:38",
      "max": "2018-09-03T17:40:06",
      "invalid": 0
    },
    "order_delivered_carrier_date": {
      "min": "2016-10-08T10:34:01",
      "max": "2018-09-11T19:48:28",
      "invalid": 0
    },
    "order_delivered_customer_date": {
      "min": "2016-10-11T13:46:32",
      "max": "2018-10-17T13:22:46",
      "invalid": 0
    },
    "order_estimated_delivery_date": {
      "min": "2016-09-30T00:00:00",
      "max": "2018-11-12T00:00:00",
      "invalid": 0
    }
  }
}
```

## olist_products_dataset.csv

```json
{
  "rows": 32951,
  "columns": [
    "product_id",
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
  ],
  "missing_cells": {
    "product_id": 0,
    "product_category_name": 610,
    "product_name_lenght": 610,
    "product_description_lenght": 610,
    "product_photos_qty": 610,
    "product_weight_g": 2,
    "product_length_cm": 2,
    "product_height_cm": 2,
    "product_width_cm": 2
  },
  "candidate_key": [
    "product_id"
  ],
  "missing_key_rows": 0,
  "duplicate_key_rows": 0
}
```

## olist_sellers_dataset.csv

```json
{
  "rows": 3095,
  "columns": [
    "seller_id",
    "seller_zip_code_prefix",
    "seller_city",
    "seller_state"
  ],
  "missing_cells": {
    "seller_id": 0,
    "seller_zip_code_prefix": 0,
    "seller_city": 0,
    "seller_state": 0
  },
  "candidate_key": [
    "seller_id"
  ],
  "missing_key_rows": 0,
  "duplicate_key_rows": 0
}
```

## product_category_name_translation.csv

```json
{
  "rows": 71,
  "columns": [
    "product_category_name",
    "product_category_name_english"
  ],
  "missing_cells": {
    "product_category_name": 0,
    "product_category_name_english": 0
  },
  "candidate_key": [
    "product_category_name"
  ],
  "missing_key_rows": 0,
  "duplicate_key_rows": 0
}
```

