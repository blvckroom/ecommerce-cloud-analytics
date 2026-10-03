with invalid_rows as (
    select customer_unique_id
    from {{ ref('mart_customer_rfm') }}
    where customer_unique_id is null
       or first_purchase_date_in_window is null
       or last_purchase_date_in_window is null
       or first_purchase_date_in_window < date '2017-01-01'
       or last_purchase_date_in_window >= date '2018-08-01'
       or first_purchase_date_in_window > last_purchase_date_in_window
       or reference_date is distinct from date '2018-08-01'
       or recency_days is null
       or recency_days < 1
       or recency_days is distinct from (
            reference_date - last_purchase_date_in_window
          )
       or frequency_orders is null
       or frequency_orders < 1
       or monetary_gmv is null
       or monetary_gmv < 0
       or customer_segment is distinct from (
            case
                when frequency_orders >= 2 and recency_days <= 90
                    then 'recent_repeat'
                when frequency_orders >= 2 and recency_days > 90
                    then 'inactive_repeat'
                when frequency_orders = 1 and recency_days <= 90
                    then 'recent_single'
                else 'inactive_single'
            end
          )
),

duplicate_customers as (
    select customer_unique_id
    from {{ ref('mart_customer_rfm') }}
    group by customer_unique_id
    having count(*) > 1
)

select * from invalid_rows
union all
select * from duplicate_customers
