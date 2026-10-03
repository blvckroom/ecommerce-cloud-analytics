with invalid_rows as (
    select
        cohort_month,
        month_number
    from {{ ref('mart_customer_cohort') }}
    where cohort_month is null
       or month_number is null
       or month_number not between 0 and 12
       or cohort_customers is null
       or cohort_customers <= 0
       or activity_month is distinct from (
            cohort_month + month_number * interval '1 month'
          )::date
       or is_observed is distinct from (
            activity_month < date '2018-08-01'
          )
       or (
            is_observed
            and (
                active_customers is null
                or active_customers < 0
                or active_customers > cohort_customers
                or retention_pct is null
                or retention_pct < 0
                or retention_pct > 100
                or abs(
                    retention_pct
                    - 100.0 * active_customers / cohort_customers
                ) > 0.000001
            )
          )
       or (
            not is_observed
            and (
                active_customers is not null
                or retention_pct is not null
            )
          )
       or (
            month_number = 0
            and (
                active_customers is distinct from cohort_customers
                or retention_pct is distinct from 100.0
            )
          )
),

duplicate_keys as (
    select
        cohort_month,
        month_number
    from {{ ref('mart_customer_cohort') }}
    group by 1, 2
    having count(*) > 1
),

incomplete_cohorts as (
    select
        cohort_month,
        -1 as month_number
    from {{ ref('mart_customer_cohort') }}
    group by cohort_month
    having count(*) <> 13
)

select * from invalid_rows
union all
select * from duplicate_keys
union all
select * from incomplete_cohorts
