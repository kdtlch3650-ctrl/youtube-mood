import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models" / "mood-roberta-small"


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Predict KOTE emotion labels from a trained local model.")
    parser.add_argument("text", help="Emotion sentence to analyze.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of labels to print.")
    return parser.parse_args()


def load_labels(path: Path) -> list[str]:
    return json.loads(path.read_text(encoding="utf-8"))


def predict(text: str, top_k: int) -> list[tuple[str, float]]:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    label_names = load_labels(MODEL_DIR / "labels.json")

    encoded = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=128,
        return_tensors="pt",
    )

    model.eval()

    with torch.no_grad():
        outputs = model(**encoded)

    # 멀티라벨 분류는 각 라벨이 켜질 확률을 따로 계산하므로 sigmoid를 사용한다.
    scores = torch.sigmoid(outputs.logits).squeeze(0)
    top_scores = torch.topk(scores, k=min(top_k, len(label_names)))

    return [
        (label_names[index], float(score))
        for index, score in zip(top_scores.indices.tolist(), top_scores.values.tolist(), strict=True)
    ]


def main() -> None:
    args = parse_args()
    predictions = predict(args.text, args.top_k)

    for label, score in predictions:
        print(f"{label}\t{score:.4f}")


if __name__ == "__main__":
    main()
