with invalid_rows as (
    select
        customer_unique_id,
        activity_month
    from {{ ref('int_customer_monthly') }}
    where customer_unique_id is null
       or activity_month is null
       or first_observed_purchase_month is null
       or delivered_orders is null
       or delivered_orders <= 0
       or merchandise_gmv is null
       or merchandise_gmv < 0
       or activity_month < first_observed_purchase_month
       or activity_month >= date '2018-08-01'
       or activity_month <> date_trunc('month', activity_month)::date
       or first_observed_purchase_month <>
          date_trunc('month', first_observed_purchase_month)::date
),

duplicate_keys as (
    select
        customer_unique_id,
        activity_month
    from {{ ref('int_customer_monthly') }}
    group by 1, 2
    having count(*) > 1
)

select * from invalid_rows
union all
select * from duplicate_keys
