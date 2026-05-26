import ast
import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
OUTPUT_PATH = BASE_DIR / "data" / "kote_training_data.jsonl"
KOTE_LABELS = [
    "불평/불만",
    "환영/호의",
    "감동/감탄",
    "지긋지긋",
    "고마움",
    "슬픔",
    "화남/분노",
    "존경",
    "기대감",
    "우쭐댐/무시함",
    "안타까움/실망",
    "비장함",
    "의심/불신",
    "뿌듯함",
    "편안/쾌적",
    "신기함/관심",
    "아껴주는",
    "부끄러움",
    "공포/무서움",
    "절망",
    "한심함",
    "역겨움/징그러움",
    "짜증",
    "어이없음",
    "없음",
    "패배/자기혐오",
    "귀찮음",
    "힘듦/지침",
    "즐거움/신남",
    "깨달음",
    "죄책감",
    "증오/혐오",
    "흐뭇함(귀여움/예쁨)",
    "당황/난처",
    "경악",
    "부담/안_내킴",
    "서러움",
    "재미없음",
    "불쌍함/연민",
    "놀람",
    "행복",
    "불안/걱정",
    "기쁨",
    "안심/신뢰",
]


def parse_labels(raw_labels: str) -> list[str]:
    """KOTE TSV의 숫자 라벨 문자열을 감정 라벨 이름으로 변환한다."""
    value = raw_labels.strip()

    if not value:
        return []

    if "," in value and "[" not in value:
        return [
            KOTE_LABELS[int(label_index)]
            for label_index in value.split(",")
            if label_index.strip().isdigit()
        ]

    try:
        labels = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return [value]

    if isinstance(labels, list):
        parsed_labels = []

        for label in labels:
            label_text = str(label).strip()

            if label_text.isdigit():
                parsed_labels.append(KOTE_LABELS[int(label_text)])
            elif label_text:
                parsed_labels.append(label_text)

        return parsed_labels

    return [str(labels).strip()]


def read_kote_tsv(path: Path) -> list[dict]:
    rows = []

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t", fieldnames=["id", "text", "labels"])

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
