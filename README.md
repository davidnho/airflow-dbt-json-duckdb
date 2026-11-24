# Airflow + dbt + CSV → JSON + DuckDB

A portfolio-ready batch ELT pipeline orchestrated by Apache Airflow and transformed with dbt.

## What it does
1. Reads sample `customers.csv` and `sales.csv`.
2. Converts CSV inputs into JSON Lines files in `data/bronze/`.
3. Uses dbt + DuckDB to clean and transform the JSON data.
4. Builds a Gold customer sales summary table.
5. Exports the Gold table to `data/gold/customer_sales_summary.json`.
6. Runs through GitHub Actions and uploads outputs as a downloadable artifact.

**Storage design:** JSON Lines files are the Bronze/Silver interchange layer. DuckDB (`data/warehouse/sales.duckdb`) is the SQL execution and analytics database used by dbt. No PostgreSQL, NeonDB, or Docker is required.

## Run in GitHub Actions
Open **Actions** → **Airflow + dbt JSON/DuckDB Pipeline** → **Run workflow**. The workflow also runs daily at 02:00 UTC (10:00 AM Philippines time). Outputs are uploaded as the `pipeline-output` artifact for 14 days. GitHub-hosted runners are temporary, so outputs are not automatically committed to the repository.

## Local setup (Windows 11, Python 3.11)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
$env:AIRFLOW_HOME = "$PWD\.airflow"
$env:PIPELINE_ROOT = "$PWD"
$env:DBT_PROFILES_DIR = "$PWD\dbt_project"
$env:DUCKDB_PATH = "$PWD\data\warehouse\sales.duckdb"
pip install "apache-airflow==2.10.5" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt"
pip install -r requirements.txt
airflow db migrate
airflow dags test sales_json_duckdb_pipeline 2026-01-01
```

## Models
| Model | Layer | Purpose |
|---|---|---|
| `stg_customers` | Staging | Typed customer records from Bronze JSONL |
| `stg_sales` | Staging | Typed sales records from Bronze JSONL |
| `customer_sales_summary` | Gold | Revenue, order count and average order value per customer |

Only COMPLETED sales are included. dbt schema tests check unique/non-null identifiers and required fields; a singular test checks for negative sale amounts.

## Notes
Airflow's metadata database is temporary and separate from DuckDB. This GitHub Actions pattern is a lightweight portfolio demonstration, not a persistent production Airflow service.
