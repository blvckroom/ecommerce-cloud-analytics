select
    date_trunc('month', purchased_at)::date as purchase_month,
    category_name,
    sum(item_price) as merchandise_gmv,
    count(*) as item_count,
    count(distinct order_id) as delivered_orders,
    count(distinct customer_unique_id) as purchasing_customers
from {{ ref('fct_order_items') }}
where order_status = 'delivered'
  and purchased_at >= timestamp '2017-01-01'
  and purchased_at < timestamp '2018-08-01'
group by 1, 2
