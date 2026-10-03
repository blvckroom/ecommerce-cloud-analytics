select
    date_trunc('month', purchased_at)::date as purchase_month,
    coalesce(customer_state, 'Unknown') as customer_state,
    sum(merchandise_value) as merchandise_gmv,
    count(*) as delivered_orders,
    count(distinct customer_unique_id) as purchasing_customers,
    sum(merchandise_value) / nullif(count(*), 0) as aov,
    count(*) filter (
        where is_late_delivery is not null
    ) as delivery_date_eligible_orders,
    count(*) filter (
        where is_late_delivery is true
    ) as late_orders
from {{ ref('fct_orders') }}
where order_status = 'delivered'
  and purchased_at >= timestamp '2017-01-01'
  and purchased_at < timestamp '2018-08-01'
group by 1, 2
