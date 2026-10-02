select
    source_row_number,
    review_id,
    order_id,
    review_score,
    review_creation_date as review_created_at,
    review_answer_timestamp as review_answered_at
from {{ source('olist_raw', 'reviews') }}
