with raw_item_totals as (
    select
        order_id,
        sum(price) as merchandise_value
    from {{ source('olist_raw', 'order_items') }}
    group by order_id
),

raw_monthly as (
    select
        date_trunc(
            'month', o.order_purchase_timestamp
        )::date as purchase_month,
        sum(i.merchandise_value) as merchandise_gmv,
        count(*) as delivered_orders,
        count(distinct c.customer_unique_id) as purchasing_customers
    from {{ source('olist_raw', 'orders') }} o
    left join raw_item_totals i on o.order_id = i.order_id
    left join {{ source('olist_raw', 'customers') }} c
        on o.customer_id = c.customer_id
    where o.order_status = 'delivered'
      and o.order_purchase_timestamp >= timestamp '2017-01-01'
      and o.order_purchase_timestamp < timestamp '2018-08-01'
    group by 1
),

expected as (
    select
        months.month_start::date as purchase_month,
        coalesce(r.merchandise_gmv, 0::numeric) as merchandise_gmv,
        coalesce(r.delivered_orders, 0::bigint) as delivered_orders,
        coalesce(r.purchasing_customers, 0::bigint) as purchasing_customers
    from generate_series(
        date '2017-01-01',
        date '2018-07-01',
        interval '1 month'
    ) as months(month_start)
    left join raw_monthly r
        on r.purchase_month = months.month_start::date
)

select
    coalesce(m.purchase_month, e.purchase_month) as purchase_month
from {{ ref('mart_sales_monthly') }} m
full outer join expected e using (purchase_month)
where m.purchase_month is null
   or e.purchase_month is null
   or m.merchandise_gmv is distinct from e.merchandise_gmv
   or m.delivered_orders is distinct from e.delivered_orders
   or m.purchasing_customers is distinct from e.purchasing_customers
   or m.aov is distinct from (
       e.merchandise_gmv / nullif(e.delivered_orders, 0)
   )
