with expected as (
    select
        o.order_id,
        not exists (
            select 1 from {{ ref('stg_payments') }} p
            where p.order_id = o.order_id
        ) as missing_payment,
        not exists (
            select 1 from {{ ref('stg_reviews') }} r
            where r.order_id = o.order_id
        ) as missing_review,
        o.delivered_at is null as missing_actual_delivery,
        case
            when o.delivered_at is not null
             and o.estimated_delivery_at is not null
            then o.delivered_at::date > o.estimated_delivery_at::date
        end as is_late_delivery
    from {{ ref('stg_orders') }} o
)
select f.order_id
from {{ ref('fct_orders') }} f
join expected e on f.order_id = e.order_id
where f.missing_payment is distinct from e.missing_payment
   or f.missing_review is distinct from e.missing_review
   or f.missing_actual_delivery is distinct from e.missing_actual_delivery
   or f.is_late_delivery is distinct from e.is_late_delivery
