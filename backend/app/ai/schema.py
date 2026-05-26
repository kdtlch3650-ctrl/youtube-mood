from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    # 사용자가 입력한 원문을 그대로 보관한다.
    input_text: str

    # AI가 판단한 감정 태그 목록
    emotions: list[str] = Field(default_factory=list)

    # AI가 판단한 분위기 태그 목록
    mood_tags: list[str] = Field(default_factory=list)

    # YouTube 검색에 사용할 키워드 목록
    search_keywords: list[str] = Field(default_factory=list)

