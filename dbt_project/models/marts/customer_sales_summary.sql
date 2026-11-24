{{ config(materialized='table') }}

with completed_sales as (
    select * from {{ ref('stg_sales') }} where status = 'COMPLETED'
),
sales_by_customer as (
    select
        customer_id,
        count(*) as total_orders,
        sum(amount) as total_revenue,
        avg(amount) as average_order_value,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date
    from completed_sales
    group by customer_id
)
select
    c.customer_id,
    c.customer_name,
    c.email,
    coalesce(s.total_orders, 0) as total_orders,
    coalesce(s.total_revenue, 0)::decimal(12, 2) as total_revenue,
    coalesce(s.average_order_value, 0)::decimal(12, 2) as average_order_value,
    s.first_order_date,
    s.last_order_date
from {{ ref('stg_customers') }} c
left join sales_by_customer s using (customer_id)
