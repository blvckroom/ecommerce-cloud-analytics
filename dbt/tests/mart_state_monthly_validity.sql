select
    purchase_month,
    customer_state,
    'duplicate_key' as issue
from {{ ref('mart_state_monthly') }}
group by purchase_month, customer_state
having count(*) > 1

union all

select
    purchase_month,
    customer_state,
    'invalid_counts' as issue
from {{ ref('mart_state_monthly') }}
where delivered_orders <= 0
   or purchasing_customers <= 0
   or purchasing_customers > delivered_orders
   or delivery_date_eligible_orders < 0
   or delivery_date_eligible_orders > delivered_orders
   or late_orders < 0
   or late_orders > delivery_date_eligible_orders
