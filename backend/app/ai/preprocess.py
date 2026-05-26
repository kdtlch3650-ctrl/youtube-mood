import re


def preprocess_text(text: str) -> str:
    # AI가 문장을 읽기 전에 기본적인 노이즈를 정리한다.
    # 공백 정리만 해도 입력이 훨씬 안정적이다.
    cleaned_text = text.strip()

    # 연속된 공백을 하나로 줄인다.
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)

    return cleaned_text

