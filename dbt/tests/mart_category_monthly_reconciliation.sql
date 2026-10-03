with expected as (
    select
        date_trunc(
            'month', o.order_purchase_timestamp
        )::date as purchase_month,
        coalesce(
            t.product_category_name_english,
            p.product_category_name,
            'Unknown'
        ) as category_name,
        sum(i.price) as merchandise_gmv,
        count(*) as item_count,
        count(distinct o.order_id) as delivered_orders,
        count(distinct c.customer_unique_id) as purchasing_customers
    from {{ source('olist_raw', 'order_items') }} i
    join {{ source('olist_raw', 'orders') }} o
        on i.order_id = o.order_id
    left join {{ source('olist_raw', 'customers') }} c
        on o.customer_id = c.customer_id
    left join {{ source('olist_raw', 'products') }} p
        on i.product_id = p.product_id
    left join {{ source('olist_raw', 'category_translation') }} t
        on p.product_category_name = t.product_category_name
    where o.order_status = 'delivered'
      and o.order_purchase_timestamp >= timestamp '2017-01-01'
      and o.order_purchase_timestamp < timestamp '2018-08-01'
    group by 1, 2
)

select
    coalesce(m.purchase_month, e.purchase_month) as purchase_month,
    coalesce(m.category_name, e.category_name) as category_name
from {{ ref('mart_category_monthly') }} m
full outer join expected e
    on m.purchase_month = e.purchase_month
   and m.category_name = e.category_name
where m.purchase_month is null
   or e.purchase_month is null
   or m.merchandise_gmv is distinct from e.merchandise_gmv
   or m.item_count is distinct from e.item_count
   or m.delivered_orders is distinct from e.delivered_orders
   or m.purchasing_customers is distinct from e.purchasing_customers
