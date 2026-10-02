with ranked as (
    select
        source_row_number,
        review_id,
        order_id,
        review_score,
        review_created_at,
        review_answered_at,
        count(*) over (
            partition by order_id
        ) as review_record_count,
        row_number() over (
            partition by order_id
            order by
                review_answered_at desc nulls last,
                review_created_at desc nulls last,
                review_id desc,
                source_row_number desc
        ) as selection_rank
    from {{ ref('stg_reviews') }}
)
select
    source_row_number,
    review_id,
    order_id,
    review_score,
    review_created_at,
    review_answered_at,
    review_record_count
from ranked
where selection_rank = 1
