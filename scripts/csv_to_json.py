import csv
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("PIPELINE_ROOT", Path(__file__).resolve().parents[1])).resolve()
INPUT_DIR = ROOT / "data" / "input"
BRONZE_DIR = ROOT / "data" / "bronze"


def convert_csv_to_jsonl(source: Path, destination: Path) -> int:
    if not source.exists():
        raise FileNotFoundError(f"Missing input file: {source}")
    count = 0
    with source.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {source}")
        with destination.open("w", encoding="utf-8") as json_file:
            for row in reader:
                json_file.write(json.dumps(row, ensure_ascii=False) + "\n")
                count += 1
    print(f"Converted {count} rows: {source.name} -> {destination}")
    return count


def main():
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    convert_csv_to_jsonl(INPUT_DIR / "customers.csv", BRONZE_DIR / "customers.jsonl")
    convert_csv_to_jsonl(INPUT_DIR / "sales.csv", BRONZE_DIR / "sales.jsonl")


if __name__ == "__main__":
    main()
