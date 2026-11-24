import json
from decimal import Decimal
import os
from pathlib import Path
import duckdb

ROOT = Path(os.environ.get("PIPELINE_ROOT", Path(__file__).resolve().parents[1])).resolve()
DB_PATH = Path(os.environ.get("DUCKDB_PATH", ROOT / "data" / "warehouse" / "sales.duckdb")).resolve()
OUTPUT = ROOT / "data" / "gold" / "customer_sales_summary.json"


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DuckDB database not found: {DB_PATH}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        rows = con.execute("""
            SELECT customer_id, customer_name, email, total_orders,
                   total_revenue, average_order_value, first_order_date, last_order_date
            FROM customer_sales_summary
            ORDER BY total_revenue DESC, customer_id
        """).fetchall()
        columns = [
            "customer_id", "customer_name", "email", "total_orders",
            "total_revenue", "average_order_value", "first_order_date", "last_order_date"
        ]
        records = [
            {key: (value.isoformat() if hasattr(value, "isoformat") else value)
             for key, value in zip(columns, row)}
            for row in rows
        ]
    finally:
        con.close()
    # DuckDB DECIMAL values are Python Decimal objects; convert them to JSON numbers.
    with OUTPUT.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False,
                  default=lambda value: float(value) if isinstance(value, Decimal) else value)
    print(f"Exported {len(records)} Gold records to {OUTPUT}")


if __name__ == "__main__":
    main()
