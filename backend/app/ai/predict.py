from app.ai.model import load_model
from app.ai.preprocess import preprocess_text
from app.ai.schema import AnalysisResult


def build_search_keywords(emotions: list[str], mood_tags: list[str]) -> list[str]:
    # 감정과 분위기 조합으로 YouTube 검색어를 만든다.
    # AI가 직접 검색어를 전부 만들기보다, 백엔드에서 규칙적으로 조합하는 편이 더 안정적이다.
    keywords: list[str] = []

    if "calm" in emotions or "soft" in mood_tags:
        keywords.append("calm soft music")

    if "tired" in emotions:
        keywords.append("tired quiet playlist")

    if "focused" in emotions or "minimal" in mood_tags:
        keywords.append("focused minimal music")

    if "angry" in emotions or "heavy" in mood_tags:
        keywords.append("angry heavy music")

    if "sad" in emotions or "warm" in mood_tags:
        keywords.append("warm relaxing music")

    # 아무 것도 잡히지 않으면 기본 검색어를 넣는다.
    if not keywords:
        keywords.append("relaxing music playlist")

    # 검색어가 너무 많아지지 않게 앞에서부터 3개만 사용한다.
    return keywords[:3]


def predict_analysis(text: str) -> AnalysisResult:
    # 1. 입력 문장을 정리한다.
    cleaned_text = preprocess_text(text)

    # 2. 모델을 불러온다.
    model = load_model()

    # 3. 모델이 감정과 분위기를 예측한다.
    predicted = model.predict(cleaned_text)
    emotions = predicted.get("emotions", [])
    mood_tags = predicted.get("mood_tags", [])

    # 4. 검색용 키워드를 만든다.
    search_keywords = build_search_keywords(emotions, mood_tags)

    # 5. 프론트와 백엔드가 함께 쓸 수 있는 형태로 반환한다.
    return AnalysisResult(
        input_text=cleaned_text,
        emotions=emotions,
        mood_tags=mood_tags,
        search_keywords=search_keywords,
    )

