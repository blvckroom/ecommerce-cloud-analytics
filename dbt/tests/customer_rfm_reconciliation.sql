with raw_item_totals as (
    select
        order_id,
        sum(price) as merchandise_gmv
    from {{ source('olist_raw', 'order_items') }}
    group by order_id
),

expected as (
    select
        c.customer_unique_id,
        min(o.order_purchase_timestamp)::date
            as first_purchase_date_in_window,
        max(o.order_purchase_timestamp)::date
            as last_purchase_date_in_window,
        count(*) as frequency_orders,
        sum(i.merchandise_gmv) as monetary_gmv
    from {{ source('olist_raw', 'orders') }} o
    join {{ source('olist_raw', 'customers') }} c
        on o.customer_id = c.customer_id
    left join raw_item_totals i
        on o.order_id = i.order_id
    where o.order_status = 'delivered'
      and o.order_purchase_timestamp >= timestamp '2017-01-01'
      and o.order_purchase_timestamp < timestamp '2018-08-01'
    group by c.customer_unique_id
),

actual as (
    select * from {{ ref('mart_customer_rfm') }}
)

select
    coalesce(e.customer_unique_id, a.customer_unique_id)
        as customer_unique_id
from expected e
full outer join actual a
    on e.customer_unique_id = a.customer_unique_id
where e.customer_unique_id is null
   or a.customer_unique_id is null
   or e.first_purchase_date_in_window
      is distinct from a.first_purchase_date_in_window
   or e.last_purchase_date_in_window
      is distinct from a.last_purchase_date_in_window
   or e.frequency_orders is distinct from a.frequency_orders
   or e.monetary_gmv is distinct from a.monetary_gmv
