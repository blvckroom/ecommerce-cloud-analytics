with customer_metrics as (
    select
        customer_unique_id,
        min(purchased_at)::date as first_purchase_date_in_window,
        max(purchased_at)::date as last_purchase_date_in_window,
        count(*) as frequency_orders,
        sum(merchandise_value) as monetary_gmv
    from {{ ref('fct_orders') }}
    where order_status = 'delivered'
      and purchased_at >= timestamp '2017-01-01'
      and purchased_at < timestamp '2018-08-01'
    group by customer_unique_id
),

recency as (
    select
        *,
        date '2018-08-01' as reference_date,
        date '2018-08-01' - last_purchase_date_in_window
            as recency_days
    from customer_metrics
)

select
    *,
    case
        when frequency_orders >= 2 and recency_days <= 90
            then 'recent_repeat'
        when frequency_orders >= 2 and recency_days > 90
            then 'inactive_repeat'
        when frequency_orders = 1 and recency_days <= 90
            then 'recent_single'
        else 'inactive_single'
    end as customer_segment
from recency
