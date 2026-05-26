import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "kote_training_data.jsonl"
MODEL_NAME = "klue/roberta-small"
OUTPUT_DIR = BASE_DIR / "models" / "mood-roberta-small"


class MoodDataset(Dataset):
    def __init__(self, texts: list[str], labels: list[list[float]], tokenizer: AutoTokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, index: int) -> dict:
        # 문장을 모델이 읽을 수 있는 토큰 숫자 배열로 바꾼다.
        encoded = self.tokenizer(
            self.texts[index],
            padding="max_length",
            truncation=True,
            max_length=128,
            return_tensors="pt",
        )

        item = {key: value.squeeze(0) for key, value in encoded.items()}
        item["labels"] = self.labels[index]
        return item


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def limit_rows(rows: list[dict], max_samples: int | None) -> list[dict]:
    if max_samples is None:
        return rows

    # 처음에는 전체 데이터가 아니라 작은 샘플로 학습 파이프라인만 검증한다.
    return rows[:max_samples]


def collect_labels(rows: list[dict]) -> list[str]:
    labels = set()

    for row in rows:
        labels.update(row["labels"])

    return sorted(labels)


def encode_labels(rows: list[dict], label_names: list[str]) -> list[list[float]]:
    label_index = {label: index for index, label in enumerate(label_names)}
    encoded_rows = []

    for row in rows:
        # 한 문장에 여러 KOTE 감정 라벨이 붙을 수 있으므로 멀티라벨 배열로 만든다.
        encoded = [0.0] * len(label_names)

        for label in row["labels"]:
            encoded[label_index[label]] = 1.0

        encoded_rows.append(encoded)

    return encoded_rows


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Train KOTE emotion classifier.")
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Use only the first N rows for a quick training pipeline test.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = limit_rows(load_jsonl(DATA_PATH), args.max_samples)
    label_names = collect_labels(rows)
    labels = encode_labels(rows, label_names)
    texts = [row["text"] for row in rows]

    train_texts, valid_texts, train_labels, valid_labels = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_dataset = MoodDataset(train_texts, train_labels, tokenizer)
    valid_dataset = MoodDataset(valid_texts, valid_labels, tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(label_names),
        problem_type="multi_label_classification",
    )

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        num_train_epochs=3,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
    )

    trainer.train()
    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))

    label_path = OUTPUT_DIR / "labels.json"
    label_path.write_text(json.dumps(label_names, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
