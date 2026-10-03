with checks as (
    select
        'item_count' as check_name,
        (select count(*) from {{ ref('fct_order_items') }}) as actual,
        (select count(*) from {{ ref('stg_order_items') }}) as expected

    union all

    select
        'merchandise_total',
        (select sum(item_price) from {{ ref('fct_order_items') }}),
        (select sum(item_price) from {{ ref('stg_order_items') }})

    union all

    select
        'freight_total',
        (select sum(freight_value) from {{ ref('fct_order_items') }}),
        (select sum(freight_value) from {{ ref('stg_order_items') }})

    union all

    select
        'analysis_window_merchandise',
        (
            select sum(item_price)
            from {{ ref('fct_order_items') }}
            where order_status = 'delivered'
              and purchased_at >= timestamp '2017-01-01'
              and purchased_at < timestamp '2018-08-01'
        ),
        (
            select sum(merchandise_value)
            from {{ ref('fct_orders') }}
            where order_status = 'delivered'
              and purchased_at >= timestamp '2017-01-01'
              and purchased_at < timestamp '2018-08-01'
        )
)
select *
from checks
where actual is distinct from expected
