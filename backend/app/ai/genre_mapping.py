import re


GENRE_KEYWORDS: dict[str, list[str]] = {
    "jazz": ["jazz", "재즈"],
    "hiphop": ["hiphop", "hip hop", "힙합", "랩"],
    "lofi": ["lofi", "lo-fi", "로파이", "로우파이"],
    "rock": ["rock", "락", "록"],
    "ballad": ["ballad", "발라드"],
    "rnb": ["rnb", "r&b", "알앤비"],
    "pop": ["pop", "팝"],
    "classical": ["classical", "클래식"],
    "edm": ["edm", "일렉", "일렉트로닉"],
    "acoustic": ["acoustic", "어쿠스틱"],
}


def _contains_keyword(text: str, keyword: str) -> bool:
    if keyword.isascii() and keyword.replace("-", "").replace("&", "").replace(" ", "").isalnum():
        return re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", text) is not None

    return keyword in text


def extract_genre(text: str) -> str | None:
    normalized_text = text.lower()
    matches: list[tuple[int, str]] = []

    for genre, keywords in GENRE_KEYWORDS.items():
        for keyword in keywords:
            normalized_keyword = keyword.lower()

            if not _contains_keyword(normalized_text, normalized_keyword):
                continue

            matches.append((normalized_text.find(normalized_keyword), genre))
            break

    if not matches:
        return None

    # 여러 장르가 같이 들어오면 사용자가 먼저 말한 장르를 우선한다.
    return min(matches, key=lambda match: match[0])[1]
