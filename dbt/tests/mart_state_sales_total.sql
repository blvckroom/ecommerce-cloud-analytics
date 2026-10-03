with state_totals as (
    select
        purchase_month,
        sum(merchandise_gmv) as merchandise_gmv,
        sum(delivered_orders) as delivered_orders
    from {{ ref('mart_state_monthly') }}
    group by purchase_month
)

select
    coalesce(r.purchase_month, s.purchase_month) as purchase_month
from state_totals r
full outer join {{ ref('mart_sales_monthly') }} s
    using (purchase_month)
where coalesce(r.merchandise_gmv, 0)
      is distinct from s.merchandise_gmv
   or coalesce(r.delivered_orders, 0)
      is distinct from s.delivered_orders
