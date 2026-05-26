import ast
import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
OUTPUT_PATH = BASE_DIR / "data" / "kote_training_data.jsonl"


def parse_labels(raw_labels: str) -> list[str]:
    """KOTE TSV의 labels 문자열을 파이썬 리스트로 변환한다."""
    value = raw_labels.strip()

    if not value:
        return []

    try:
        labels = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return [value]

    if isinstance(labels, list):
        return [str(label).strip() for label in labels if str(label).strip()]

    return [str(labels).strip()]


def read_kote_tsv(path: Path) -> list[dict]:
    rows = []

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            text = row.get("text", "").strip()
            labels = parse_labels(row.get("labels", ""))

            # 텍스트나 라벨이 없는 행은 학습에 사용할 수 없으므로 제외한다.
            if not text or not labels:
                continue

            rows.append({"text": text, "labels": labels})

    return rows


def collect_training_rows() -> list[dict]:
    rows = []

    for split_name in ("train", "val", "test"):
        path = RAW_DATA_DIR / f"{split_name}.tsv"

        if not path.exists():
            continue

        rows.extend(read_kote_tsv(path))

    return rows


def write_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    rows = collect_training_rows()

    if not rows:
        raise FileNotFoundError(
            "KOTE TSV 파일을 찾지 못했습니다. "
            "ml/data/raw/ 폴더에 train.tsv, val.tsv, test.tsv 중 하나 이상을 넣어주세요."
        )

    write_jsonl(rows, OUTPUT_PATH)
    print(f"converted {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
