with expected as (
    select
        order_id,
        order_delivered_customer_date is not null
            and order_estimated_delivery_date is not null
            as delivery_date_eligible,
        case
            when order_delivered_customer_date is not null
             and order_estimated_delivery_date is not null
            then order_delivered_customer_date::date
                 - order_estimated_delivery_date::date
        end as delivery_delay_calendar_days
    from {{ source('olist_raw', 'orders') }}
    where order_status = 'delivered'
      and order_purchase_timestamp >= timestamp '2017-01-01'
      and order_purchase_timestamp < timestamp '2018-08-01'
)

select coalesce(m.order_id, e.order_id) as order_id
from {{ ref('mart_delivery_orders') }} m
full outer join expected e using (order_id)
where m.order_id is null
   or e.order_id is null
   or m.delivery_date_eligible
      is distinct from e.delivery_date_eligible
   or m.delivery_delay_calendar_days
      is distinct from e.delivery_delay_calendar_days
