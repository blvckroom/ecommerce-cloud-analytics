with customer_cohorts as (
    select
        customer_unique_id,
        min(activity_month) as cohort_month
    from {{ ref('int_customer_monthly') }}
    group by customer_unique_id
),

cohort_sizes as (
    select
        cohort_month,
        count(*) as cohort_customers
    from customer_cohorts
    group by cohort_month
),

activity as (
    select
        c.cohort_month,
        m.activity_month,
        count(*) as active_customers
    from {{ ref('int_customer_monthly') }} m
    join customer_cohorts c
        on m.customer_unique_id = c.customer_unique_id
    group by 1, 2
),

cohort_grid as (
    select
        c.cohort_month,
        c.cohort_customers,
        g.month_number,
        (
            c.cohort_month
            + g.month_number * interval '1 month'
        )::date as activity_month
    from cohort_sizes c
    cross join generate_series(0, 12) as g(month_number)
)

select
    g.cohort_month,
    g.month_number,
    g.activity_month,
    g.cohort_customers,
    g.activity_month < date '2018-08-01' as is_observed,
    case
        when g.activity_month < date '2018-08-01'
        then coalesce(a.active_customers, 0)
    end as active_customers,
    case
        when g.activity_month < date '2018-08-01'
        then 100.0 * coalesce(a.active_customers, 0)
             / nullif(g.cohort_customers, 0)
    end as retention_pct
from cohort_grid g
left join activity a
    on g.cohort_month = a.cohort_month
   and g.activity_month = a.activity_month
