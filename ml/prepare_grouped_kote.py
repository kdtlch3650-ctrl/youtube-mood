import json
from pathlib import Path

from grouped_labels import convert_kote_labels_to_groups


BASE_DIR = Path(__file__).resolve().parent
SOURCE_PATH = BASE_DIR / "data" / "kote_training_data.jsonl"
OUTPUT_PATH = BASE_DIR / "data" / "grouped_kote_training_data.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    rows = load_jsonl(SOURCE_PATH)
    grouped_rows = []

    for row in rows:
        grouped_rows.append({
            "text": row["text"],
            "labels": convert_kote_labels_to_groups(row["labels"]),
        })

    write_jsonl(OUTPUT_PATH, grouped_rows)
    print(f"created {OUTPUT_PATH}")
    print(f"rows {len(grouped_rows)}")


if __name__ == "__main__":
    main()
