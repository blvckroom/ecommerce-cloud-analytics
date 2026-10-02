select
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_state,
    o.order_status,
    o.purchased_at,
    o.approved_at,
    o.carrier_received_at,
    o.delivered_at,
    o.estimated_delivery_at,

    i.item_count,
    i.distinct_product_count,
    i.distinct_seller_count,
    i.merchandise_value,
    i.freight_value,

    p.payment_record_count,
    p.payment_value,

    r.review_id,
    r.source_row_number as selected_review_source_row,
    r.review_score,
    r.review_created_at,
    r.review_answered_at,
    r.review_record_count,

    i.order_id is null as missing_items,
    p.order_id is null as missing_payment,
    r.order_id is null as missing_review,

    o.delivered_at is null as missing_actual_delivery,
    o.estimated_delivery_at is null as missing_estimated_delivery,

    case
        when o.delivered_at is not null
         and o.estimated_delivery_at is not null
        then o.delivered_at::date > o.estimated_delivery_at::date
    end as is_late_delivery,

    case
        when o.delivered_at >= o.purchased_at
        then extract(epoch from (o.delivered_at - o.purchased_at))
             / 86400.0
    end as delivery_days,

    case
        when o.carrier_received_at is not null
        then o.carrier_received_at < o.purchased_at
    end as carrier_before_purchase,

    case
        when o.delivered_at is not null
         and o.carrier_received_at is not null
        then o.delivered_at < o.carrier_received_at
    end as delivery_before_carrier,

    case
        when r.review_answered_at is not null
         and o.delivered_at is not null
        then r.review_answered_at < o.delivered_at
    end as review_answer_before_delivery,

    p.payment_value - i.merchandise_value - i.freight_value
        as payment_reconciliation_difference

from {{ ref('stg_orders') }} as o
left join {{ ref('stg_customers') }} as c
    on o.customer_id = c.customer_id
left join {{ ref('int_order_item_totals') }} as i
    on o.order_id = i.order_id
left join {{ ref('int_order_payment_totals') }} as p
    on o.order_id = p.order_id
left join {{ ref('int_order_review_selected') }} as r
    on o.order_id = r.order_id
