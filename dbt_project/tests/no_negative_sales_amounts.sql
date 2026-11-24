select *
from {{ ref('stg_sales') }}
where amount < 0
