with monthly_activity as (
    select
        customer_unique_id,
        date_trunc('month', purchased_at)::date as activity_month,
        count(*) as delivered_orders,
        sum(merchandise_value) as merchandise_gmv
    from {{ ref('fct_orders') }}
    where order_status = 'delivered'
      and purchased_at < timestamp '2018-08-01'
    group by 1, 2
)

select
    customer_unique_id,
    activity_month,
    delivered_orders,
    merchandise_gmv,
    min(activity_month) over (
        partition by customer_unique_id
    ) as first_observed_purchase_month
from monthly_activity
