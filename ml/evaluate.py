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
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        default=None,
        help="Compare multiple thresholds, for example: --thresholds 0.3 0.4 0.5",
    )
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


def predict_scores(rows: list[dict]) -> tuple[list[list[int]], list[list[float]]]:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    label_names = load_labels(MODEL_DIR / "labels.json")
    true_labels = encode_labels(rows, label_names)
    predicted_scores = []

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

        scores = torch.sigmoid(outputs.logits).squeeze(0)
        predicted_scores.append(scores.tolist())

    return true_labels, predicted_scores


def apply_threshold(scores: list[list[float]], threshold: float) -> list[list[int]]:
    # threshold 이상인 라벨을 모델이 선택한 감정으로 본다.
    return [[1 if score >= threshold else 0 for score in row] for row in scores]


def print_metrics(true_labels: list[list[int]], predicted_labels: list[list[int]], threshold: float) -> None:
    print(f"threshold\t{threshold}")
    print(f"precision_micro\t{precision_score(true_labels, predicted_labels, average='micro', zero_division=0):.4f}")
    print(f"recall_micro\t{recall_score(true_labels, predicted_labels, average='micro', zero_division=0):.4f}")
    print(f"f1_micro\t{f1_score(true_labels, predicted_labels, average='micro', zero_division=0):.4f}")
    print(f"f1_macro\t{f1_score(true_labels, predicted_labels, average='macro', zero_division=0):.4f}")


def main() -> None:
    args = parse_args()
    rows = load_jsonl(DATA_PATH)[: args.max_samples]
    _, valid_rows = train_test_split(rows, test_size=0.2, random_state=42)
    true_labels, predicted_scores = predict_scores(valid_rows)
    thresholds = args.thresholds if args.thresholds else [args.threshold]

    print(f"samples\t{len(valid_rows)}")

    for index, threshold in enumerate(thresholds):
        if index > 0:
            print()

        predicted_labels = apply_threshold(predicted_scores, threshold)
        print_metrics(true_labels, predicted_labels, threshold)


if __name__ == "__main__":
    main()
