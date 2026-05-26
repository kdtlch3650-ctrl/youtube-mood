import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = PROJECT_ROOT / "ml" / "models" / "mood-roberta-small"
DEFAULT_THRESHOLD = 0.3


class KoteModelAdapter:
    def __init__(self, model_dir: Path = MODEL_DIR, threshold: float = DEFAULT_THRESHOLD):
        # torch/transformers는 백엔드 기본 의존성이 아니므로 모델 사용 시점에만 불러온다.
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.model_dir = model_dir
        self.threshold = threshold
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.labels = self._load_labels(model_dir / "labels.json")
        self.model.eval()

    @staticmethod
    def is_available(model_dir: Path = MODEL_DIR) -> bool:
        return (
            (model_dir / "model.safetensors").exists()
            and (model_dir / "tokenizer.json").exists()
            and (model_dir / "labels.json").exists()
        )

    @staticmethod
    def _load_labels(path: Path) -> list[str]:
        return json.loads(path.read_text(encoding="utf-8"))

    def predict(self, text: str) -> dict[str, list[str]]:
        import torch

        encoded = self.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=128,
            return_tensors="pt",
        )

        with torch.no_grad():
            outputs: Any = self.model(**encoded)

        # KOTE 모델은 여러 감정이 동시에 켜질 수 있으므로 sigmoid와 threshold를 사용한다.
        scores = torch.sigmoid(outputs.logits).squeeze(0)
        emotions = [
            self.labels[index]
            for index, score in enumerate(scores.tolist())
            if score >= self.threshold
        ]

        if not emotions:
            top_index = int(torch.argmax(scores).item())
            emotions = [self.labels[top_index]]

        return {"emotions": emotions}
