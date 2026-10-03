select
    purchase_month,
    category_name,
    count(*) as row_count
from {{ ref('mart_category_monthly') }}
group by purchase_month, category_name
having count(*) > 1
