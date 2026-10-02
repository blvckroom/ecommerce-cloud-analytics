with calendar as (
    select month_start::date as purchase_month
    from generate_series(
        date '2017-01-01',
        date '2018-07-01',
        interval '1 month'
    ) as months(month_start)
),

monthly as (
    select
        date_trunc('month', purchased_at)::date as purchase_month,
        sum(merchandise_value) as merchandise_gmv,
        count(*) as delivered_orders,
        count(distinct customer_unique_id) as purchasing_customers
    from {{ ref('fct_orders') }}
    where order_status = 'delivered'
      and purchased_at >= timestamp '2017-01-01'
      and purchased_at < timestamp '2018-08-01'
    group by 1
),

complete_months as (
    select
        c.purchase_month,
        coalesce(m.merchandise_gmv, 0::numeric) as merchandise_gmv,
        coalesce(m.delivered_orders, 0::bigint) as delivered_orders,
        coalesce(m.purchasing_customers, 0::bigint) as purchasing_customers
    from calendar c
    left join monthly m using (purchase_month)
),

with_previous as (
    select
        *,
        lag(merchandise_gmv) over (
            order by purchase_month
        ) as previous_month_gmv
    from complete_months
)

select
    purchase_month,
    merchandise_gmv,
    delivered_orders,
    purchasing_customers,
    merchandise_gmv / nullif(delivered_orders, 0) as aov,
    previous_month_gmv,
    (
        merchandise_gmv / nullif(previous_month_gmv, 0) - 1
    ) * 100 as gmv_mom_growth_pct
from with_previous
