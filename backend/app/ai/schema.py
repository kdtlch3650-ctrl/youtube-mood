from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    # 사용자가 입력한 원문을 그대로 보관한다.
    input_text: str

    # AI가 판단한 감정 태그 목록
    emotions: list[str] = Field(default_factory=list)

    # AI가 판단한 분위기 태그 목록
    mood_tags: list[str] = Field(default_factory=list)

    # 사용자가 직접 말한 음악 장르가 있으면 검색어 생성에 반영한다.
    genre: str | None = None

    # YouTube 검색에 사용할 키워드 목록
    search_keywords: list[str] = Field(default_factory=list)
