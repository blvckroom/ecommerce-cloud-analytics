select
    'order_items' as model_name,
    order_id,
    order_item_id as sequence_id,
    count(*) as row_count
from {{ ref('stg_order_items') }}
group by order_id, order_item_id
having count(*) > 1

union all

select
    'payments' as model_name,
    order_id,
    payment_sequential as sequence_id,
    count(*) as row_count
from {{ ref('stg_payments') }}
group by order_id, payment_sequential
having count(*) > 1
