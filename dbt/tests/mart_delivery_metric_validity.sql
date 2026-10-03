select order_id
from {{ ref('mart_delivery_orders') }}
where
    is_late_delivery is distinct from (
        delivery_delay_calendar_days > 0
    )
    or days_late is distinct from (
        case
            when delivery_delay_calendar_days is not null
            then greatest(delivery_delay_calendar_days, 0)
        end
    )
    or is_low_rating is distinct from (
        review_score <= 2
    )
    or missing_review is distinct from (
        review_score is null
    )
    or delivery_days < 0
    or promised_delivery_days < 0
