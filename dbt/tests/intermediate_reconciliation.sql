with checks as (
    select
        'merchandise_total' as check_name,
        (select sum(merchandise_value)
         from {{ ref('int_order_item_totals') }}) as actual,
        (select sum(item_price)
         from {{ ref('stg_order_items') }}) as expected

    union all

    select
        'freight_total',
        (select sum(freight_value)
         from {{ ref('int_order_item_totals') }}),
        (select sum(freight_value)
         from {{ ref('stg_order_items') }})

    union all

    select
        'payment_total',
        (select sum(payment_value)
         from {{ ref('int_order_payment_totals') }}),
        (select sum(payment_value)
         from {{ ref('stg_payments') }})

    union all

    select
        'item_record_count',
        (select sum(item_count)
         from {{ ref('int_order_item_totals') }}),
        (select count(*)
         from {{ ref('stg_order_items') }})

    union all

    select
        'payment_record_count',
        (select sum(payment_record_count)
         from {{ ref('int_order_payment_totals') }}),
        (select count(*)
         from {{ ref('stg_payments') }})

    union all

    select
        'selected_review_order_count',
        (select count(*)
         from {{ ref('int_order_review_selected') }}),
        (select count(distinct order_id)
         from {{ ref('stg_reviews') }})

    union all

    select
        'review_record_count',
        (select sum(review_record_count)
         from {{ ref('int_order_review_selected') }}),
        (select count(*)
         from {{ ref('stg_reviews') }})
)
select *
from checks
where actual is distinct from expected
