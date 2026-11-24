{{ config(materialized='view') }}

select
    cast(customer_id as integer) as customer_id,
    trim(customer_name) as customer_name,
    lower(trim(email)) as email,
    cast(signup_date as date) as signup_date
from read_json_auto('{{ env_var("PIPELINE_ROOT", ".") }}/data/bronze/customers.jsonl', format='newline_delimited')
