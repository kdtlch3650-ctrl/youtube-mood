from dataclasses import dataclass

from app.ai.labels import EMOTION_LABELS, MOOD_LABELS


def _dedupe(items: list[str]) -> list[str]:
    # 같은 태그가 여러 번 들어가면 화면과 검색어가 지저분해지므로 중복을 제거한다.
    return list(dict.fromkeys(items))


@dataclass
class AiModel:
    # 모델 이름을 명시해두면 나중에 교체할 때 추적하기 쉽다.
    name: str = "mood-analyzer"

    def predict(self, text: str) -> dict[str, list[str]]:
        # 지금은 실제 학습 모델 대신 규칙 기반 초안을 사용한다.
        # 나중에 학습된 모델 파일을 연결하면 이 부분만 교체하면 된다.
        normalized_text = text.lower()

        emotions: list[str] = []
        mood_tags: list[str] = []

        # 감정 키워드가 포함되면 대표 태그를 넣는다.
        if any(keyword in normalized_text for keyword in ["지쳤", "피곤", "힘들", "지침", "번아웃"]):
            emotions.extend(["tired", "calm"])
            mood_tags.extend(["soft", "quiet"])

        if any(keyword in normalized_text for keyword in ["불안", "걱정", "초조", "긴장"]):
            emotions.append("anxious")
            mood_tags.extend(["soft", "quiet"])

        if any(keyword in normalized_text for keyword in ["집중", "집중이", "몰입"]):
            emotions.append("focused")
            mood_tags.extend(["minimal", "quiet"])

        if any(keyword in normalized_text for keyword in ["화남", "짜증", "답답", "열받", "분노"]):
            emotions.extend(["angry", "stressed"])
            mood_tags.extend(["heavy", "uplifting"])

        if any(keyword in normalized_text for keyword in ["슬픔", "우울", "서럽", "가라앉"]):
            emotions.append("sad")
            mood_tags.extend(["warm", "soft"])

        if any(keyword in normalized_text for keyword in ["기쁘", "좋아", "행복", "신나", "설렘"]):
            emotions.append("happy")
            mood_tags.extend(["uplifting", "light"])

        # 아무 감정도 잡히지 않으면 차분한 기본값을 준다.
        if not emotions:
            emotions.append("calm")
        if not mood_tags:
            mood_tags.append("soft")

        # 라벨 목록에 없는 값은 나중에 제거하기 쉽도록 한 번 더 정리한다.
        emotions = [label for label in _dedupe(emotions) if label in EMOTION_LABELS]
        mood_tags = [label for label in _dedupe(mood_tags) if label in MOOD_LABELS]

        return {
            "emotions": emotions,
            "mood_tags": mood_tags,
        }


def load_model() -> AiModel:
    # 모델 로딩 로직을 한곳에 모아두면 나중에 교체하기 쉽다.
    return AiModel()

