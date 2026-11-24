from datetime import datetime, timedelta
import os
import subprocess
import sys
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

ROOT = Path(os.environ.get("PIPELINE_ROOT", Path(__file__).resolve().parents[1])).resolve()
DBT_PROJECT = ROOT / "dbt_project"
PROFILES_DIR = Path(os.environ.get("DBT_PROFILES_DIR", DBT_PROJECT)).resolve()
PYTHON = sys.executable


def run_script(script_name):
    subprocess.run([PYTHON, str(ROOT / "scripts" / script_name)], cwd=ROOT, check=True)


def run_dbt():
    env = os.environ.copy()
    env["PIPELINE_ROOT"] = str(ROOT)
    env["DUCKDB_PATH"] = str(ROOT / "data" / "warehouse" / "sales.duckdb")
    subprocess.run(
        ["dbt", "build", "--project-dir", str(DBT_PROJECT), "--profiles-dir", str(PROFILES_DIR)],
        cwd=ROOT, env=env, check=True,
    )


with DAG(
    dag_id="sales_json_duckdb_pipeline",
    description="CSV to Bronze JSONL, dbt transformations in DuckDB, and Gold JSON export",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"owner": "portfolio", "retries": 1, "retry_delay": timedelta(minutes=2)},
    tags=["portfolio", "csv", "json", "dbt", "duckdb"],
) as dag:
    ingest = PythonOperator(
        task_id="ingest_csv_to_bronze_json",
        python_callable=run_script,
        op_args=["csv_to_json.py"],
    )
    transform = PythonOperator(task_id="dbt_build", python_callable=run_dbt)
    export = PythonOperator(
        task_id="export_gold_json",
        python_callable=run_script,
        op_args=["export_gold.py"],
    )
    ingest >> transform >> export
