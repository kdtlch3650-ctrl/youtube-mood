from app.ai.model import load_model
from app.ai.mood_mapping import build_mood_tags, build_search_keywords
from app.ai.preprocess import preprocess_text
from app.ai.schema import AnalysisResult


def predict_analysis(text: str) -> AnalysisResult:
    # 1. 입력 문장을 정리한다.
    cleaned_text = preprocess_text(text)

    # 2. 모델을 불러온다.
    model = load_model()

    # 3. 모델은 감정을 예측하고, 분위기 태그는 서비스 매핑으로 만든다.
    predicted = model.predict(cleaned_text)
    emotions = predicted.get("emotions", [])
    mood_tags = predicted.get("mood_tags") or build_mood_tags(emotions)

    # 4. 검색용 키워드를 만든다.
    search_keywords = build_search_keywords(emotions, mood_tags)

    # 5. 프론트와 백엔드가 함께 쓸 수 있는 형태로 반환한다.
    return AnalysisResult(
        input_text=cleaned_text,
        emotions=emotions,
        mood_tags=mood_tags,
        search_keywords=search_keywords,
    )
