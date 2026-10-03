with category_totals as (
    select
        purchase_month,
        sum(merchandise_gmv) as merchandise_gmv
    from {{ ref('mart_category_monthly') }}
    group by purchase_month
)

select
    coalesce(c.purchase_month, s.purchase_month) as purchase_month
from category_totals c
full outer join {{ ref('mart_sales_monthly') }} s
    using (purchase_month)
where coalesce(c.merchandise_gmv, 0)
      is distinct from s.merchandise_gmv
