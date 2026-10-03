select
    order_id,
    customer_unique_id,
    customer_state,
    purchased_at,
    delivered_at,
    estimated_delivery_at,
    merchandise_value,
    delivery_days,
    is_late_delivery,

    delivered_at is not null
        and estimated_delivery_at is not null
        as delivery_date_eligible,

    case
        when delivered_at is not null
         and estimated_delivery_at is not null
        then delivered_at::date - estimated_delivery_at::date
    end as delivery_delay_calendar_days,

    case
        when delivered_at is not null
         and estimated_delivery_at is not null
        then greatest(
            delivered_at::date - estimated_delivery_at::date,
            0
        )
    end as days_late,

    case
        when estimated_delivery_at >= purchased_at
        then extract(epoch from (
            estimated_delivery_at - purchased_at
        )) / 86400.0
    end as promised_delivery_days,

    review_score,
    review_answered_at,
    review_record_count,
    missing_review,
    review_answer_before_delivery,

    case
        when review_score is not null
        then review_score <= 2
    end as is_low_rating,

    carrier_before_purchase,
    delivery_before_carrier

from {{ ref('fct_orders') }}
where order_status = 'delivered'
  and purchased_at >= timestamp '2017-01-01'
  and purchased_at < timestamp '2018-08-01'
