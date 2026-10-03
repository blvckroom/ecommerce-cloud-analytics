with raw_item_totals as (
    select
        order_id,
        sum(price) as merchandise_gmv
    from {{ source('olist_raw', 'order_items') }}
    group by order_id
),

expected_monthly as (
    select
        c.customer_unique_id,
        date_trunc('month', o.order_purchase_timestamp)::date
            as activity_month,
        count(*) as delivered_orders,
        sum(i.merchandise_gmv) as merchandise_gmv
    from {{ source('olist_raw', 'orders') }} o
    join {{ source('olist_raw', 'customers') }} c
        on o.customer_id = c.customer_id
    left join raw_item_totals i
        on o.order_id = i.order_id
    where o.order_status = 'delivered'
      and o.order_purchase_timestamp < timestamp '2018-08-01'
    group by 1, 2
),

expected as (
    select
        *,
        min(activity_month) over (
            partition by customer_unique_id
        ) as first_observed_purchase_month
    from expected_monthly
),

actual as (
    select * from {{ ref('int_customer_monthly') }}
)

select
    coalesce(e.customer_unique_id, a.customer_unique_id)
        as customer_unique_id,
    coalesce(e.activity_month, a.activity_month) as activity_month
from expected e
full outer join actual a
    on e.customer_unique_id = a.customer_unique_id
   and e.activity_month = a.activity_month
where e.customer_unique_id is null
   or a.customer_unique_id is null
   or e.delivered_orders is distinct from a.delivered_orders
   or e.merchandise_gmv is distinct from a.merchandise_gmv
   or e.first_observed_purchase_month
      is distinct from a.first_observed_purchase_month
