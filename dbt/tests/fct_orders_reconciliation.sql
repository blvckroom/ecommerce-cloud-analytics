with checks as (
    select
        'order_count' as check_name,
        (select count(*) from {{ ref('fct_orders') }}) as actual,
        (select count(*) from {{ ref('stg_orders') }}) as expected

    union all

    select
        'merchandise_total',
        (select sum(merchandise_value) from {{ ref('fct_orders') }}),
        (select sum(item_price) from {{ ref('stg_order_items') }})

    union all

    select
        'freight_total',
        (select sum(freight_value) from {{ ref('fct_orders') }}),
        (select sum(freight_value) from {{ ref('stg_order_items') }})

    union all

    select
        'payment_total',
        (select sum(payment_value) from {{ ref('fct_orders') }}),
        (select sum(payment_value) from {{ ref('stg_payments') }})

    union all

    select
        'review_order_count',
        (select count(*) from {{ ref('fct_orders') }}
         where not missing_review),
        (select count(*) from {{ ref('int_order_review_selected') }})
)
select *
from checks
where actual is distinct from expected
