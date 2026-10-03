with item_totals as (
    select order_id, sum(price) as merchandise_value
    from {{ source('olist_raw', 'order_items') }}
    group by order_id
),

expected as (
    select
        date_trunc(
            'month', o.order_purchase_timestamp
        )::date as purchase_month,
        coalesce(c.customer_state, 'Unknown') as customer_state,
        sum(i.merchandise_value) as merchandise_gmv,
        count(*) as delivered_orders,
        count(distinct c.customer_unique_id) as purchasing_customers,
        count(*) filter (
            where o.order_delivered_customer_date is not null
              and o.order_estimated_delivery_date is not null
        ) as delivery_date_eligible_orders,
        count(*) filter (
            where o.order_delivered_customer_date::date
                  > o.order_estimated_delivery_date::date
        ) as late_orders
    from {{ source('olist_raw', 'orders') }} o
    left join item_totals i on o.order_id = i.order_id
    left join {{ source('olist_raw', 'customers') }} c
        on o.customer_id = c.customer_id
    where o.order_status = 'delivered'
      and o.order_purchase_timestamp >= timestamp '2017-01-01'
      and o.order_purchase_timestamp < timestamp '2018-08-01'
    group by 1, 2
)

select
    coalesce(m.purchase_month, e.purchase_month) as purchase_month,
    coalesce(m.customer_state, e.customer_state) as customer_state
from {{ ref('mart_state_monthly') }} m
full outer join expected e
    on m.purchase_month = e.purchase_month
   and m.customer_state = e.customer_state
where m.purchase_month is null
   or e.purchase_month is null
   or m.merchandise_gmv is distinct from e.merchandise_gmv
   or m.delivered_orders is distinct from e.delivered_orders
   or m.purchasing_customers is distinct from e.purchasing_customers
   or m.aov is distinct from (
       e.merchandise_gmv / nullif(e.delivered_orders, 0)
   )
   or m.delivery_date_eligible_orders
      is distinct from e.delivery_date_eligible_orders
   or m.late_orders is distinct from e.late_orders
