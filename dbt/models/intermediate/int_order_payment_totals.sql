select
    order_id,
    count(*) as payment_record_count,
    sum(payment_value) as payment_value
from {{ ref('stg_payments') }}
group by order_id
