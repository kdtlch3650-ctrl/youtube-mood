import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

import torch
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from transformers import AutoModelForSequenceClassification, AutoTokenizer


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "kote_training_data.jsonl"
MODEL_DIR = BASE_DIR / "models" / "mood-roberta-small"


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Evaluate trained KOTE emotion classifier.")
    parser.add_argument("--max-samples", type=int, default=200, help="Use only the first N rows for quick evaluation.")
    parser.add_argument("--threshold", type=float, default=0.5, help="Prediction threshold for multi-label scores.")
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def load_labels(path: Path) -> list[str]:
    return json.loads(path.read_text(encoding="utf-8"))


def encode_labels(rows: list[dict], label_names: list[str]) -> list[list[int]]:
    label_index = {label: index for index, label in enumerate(label_names)}
    encoded_rows = []

    for row in rows:
        encoded = [0] * len(label_names)

        for label in row["labels"]:
            if label in label_index:
                encoded[label_index[label]] = 1

        encoded_rows.append(encoded)

    return encoded_rows


def predict_rows(rows: list[dict], threshold: float) -> tuple[list[list[int]], list[list[int]]]:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    label_names = load_labels(MODEL_DIR / "labels.json")
    true_labels = encode_labels(rows, label_names)
    predicted_labels = []

    model.eval()

    for row in rows:
        encoded = tokenizer(
            row["text"],
            padding="max_length",
            truncation=True,
            max_length=128,
            return_tensors="pt",
        )

        with torch.no_grad():
            outputs = model(**encoded)

        # threshold 이상인 라벨을 모델이 선택한 감정으로 본다.
        scores = torch.sigmoid(outputs.logits).squeeze(0)
        predicted_labels.append([1 if score >= threshold else 0 for score in scores.tolist()])

    return true_labels, predicted_labels


def main() -> None:
    args = parse_args()
    rows = load_jsonl(DATA_PATH)[: args.max_samples]
    _, valid_rows = train_test_split(rows, test_size=0.2, random_state=42)
    true_labels, predicted_labels = predict_rows(valid_rows, args.threshold)

    print(f"samples\t{len(valid_rows)}")
    print(f"threshold\t{args.threshold}")
    print(f"precision_micro\t{precision_score(true_labels, predicted_labels, average='micro', zero_division=0):.4f}")
    print(f"recall_micro\t{recall_score(true_labels, predicted_labels, average='micro', zero_division=0):.4f}")
    print(f"f1_micro\t{f1_score(true_labels, predicted_labels, average='micro', zero_division=0):.4f}")
    print(f"f1_macro\t{f1_score(true_labels, predicted_labels, average='macro', zero_division=0):.4f}")


if __name__ == "__main__":
    main()
