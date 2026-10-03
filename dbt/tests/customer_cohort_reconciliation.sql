with raw_customer_months as (
    select distinct
        c.customer_unique_id,
        date_trunc('month', o.order_purchase_timestamp)::date
            as activity_month
    from {{ source('olist_raw', 'orders') }} o
    join {{ source('olist_raw', 'customers') }} c
        on o.customer_id = c.customer_id
    where o.order_status = 'delivered'
      and o.order_purchase_timestamp < timestamp '2018-08-01'
),

raw_cohorts as (
    select
        customer_unique_id,
        min(activity_month) as cohort_month
    from raw_customer_months
    group by customer_unique_id
),

raw_sizes as (
    select
        cohort_month,
        count(*) as cohort_customers
    from raw_cohorts
    group by cohort_month
),

raw_activity as (
    select
        c.cohort_month,
        m.activity_month,
        count(*) as active_customers
    from raw_customer_months m
    join raw_cohorts c
        on m.customer_unique_id = c.customer_unique_id
    group by 1, 2
),

expected as (
    select
        s.cohort_month,
        g.month_number,
        s.cohort_customers,
        case
            when (
                s.cohort_month + g.month_number * interval '1 month'
            )::date < date '2018-08-01'
            then coalesce(a.active_customers, 0)
        end as active_customers
    from raw_sizes s
    cross join generate_series(0, 12) as g(month_number)
    left join raw_activity a
        on a.cohort_month = s.cohort_month
       and a.activity_month = (
            s.cohort_month + g.month_number * interval '1 month'
       )::date
),

actual as (
    select * from {{ ref('mart_customer_cohort') }}
)

select
    coalesce(e.cohort_month, a.cohort_month) as cohort_month,
    coalesce(e.month_number, a.month_number) as month_number
from expected e
full outer join actual a
    on e.cohort_month = a.cohort_month
   and e.month_number = a.month_number
where e.cohort_month is null
   or a.cohort_month is null
   or e.cohort_customers is distinct from a.cohort_customers
   or e.active_customers is distinct from a.active_customers
