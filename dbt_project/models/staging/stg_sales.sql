{{ config(materialized='view') }}

select
    cast(order_id as integer) as order_id,
    cast(customer_id as integer) as customer_id,
    cast(order_date as date) as order_date,
    cast(amount as decimal(12, 2)) as amount,
    upper(trim(status)) as status
from read_json_auto('{{ env_var("PIPELINE_ROOT", ".") }}/data/bronze/sales.jsonl', format='newline_delimited')
