select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date as shipping_limit_at,
    price as item_price,
    freight_value
from {{ source('olist_raw', 'order_items') }}
