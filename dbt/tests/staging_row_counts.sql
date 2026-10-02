{% set tables = [
    ('stg_customers', 'customers'),
    ('stg_orders', 'orders'),
    ('stg_order_items', 'order_items'),
    ('stg_payments', 'payments'),
    ('stg_reviews', 'reviews'),
    ('stg_products', 'products'),
    ('stg_sellers', 'sellers'),
    ('stg_category_translation', 'category_translation')
] %}

{% for model, raw_table in tables %}
select
    '{{ model }}' as model_name,
    (select count(*) from {{ ref(model) }}) as staging_rows,
    (select count(*) from {{ source('olist_raw', raw_table) }}) as raw_rows
where
    (select count(*) from {{ ref(model) }})
    <>
    (select count(*) from {{ source('olist_raw', raw_table) }})
{% if not loop.last %} union all {% endif %}
{% endfor %}
