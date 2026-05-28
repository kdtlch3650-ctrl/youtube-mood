import re


SAFE_GENRE_KEYWORDS: dict[str, list[str]] = {
    "jazz": ["jazz", "재즈"],
    "hiphop": ["hiphop", "hip hop", "힙합", "랩"],
    "lofi": ["lofi", "lo-fi", "로파이", "로우파이"],
    "ballad": ["ballad", "발라드"],
    "rnb": ["rnb", "r&b", "알앤비"],
    "classical": ["classical", "클래식"],
    "edm": ["edm", "일렉", "일렉트로닉"],
    "acoustic": ["acoustic", "어쿠스틱"],
    "kpop": ["kpop", "k-pop", "케이팝", "케이 pop"],
    "citypop": ["citypop", "city pop", "시티팝"],
    "ambient": ["ambient", "앰비언트"],
    "metal": ["metal", "메탈"],
    "reggae": ["reggae", "레게"],
    "ost": ["ost", "오에스티", "사운드트랙"],
}

AMBIGUOUS_GENRE_KEYWORDS: dict[str, list[str]] = {
    "rock": ["rock", "락", "록"],
    "pop": ["pop", "팝"],
    "indie": ["indie", "인디"],
    "funk": ["funk", "펑크"],
    "soul": ["soul", "소울"],
    "blues": ["blues", "블루스"],
    "punk": ["punk", "펑크락", "펑크 록"],
    "house": ["house", "하우스"],
    "techno": ["techno", "테크노"],
    "trap": ["trap", "트랩"],
    "dance": ["dance", "댄스"],
    "folk": ["folk", "포크"],
}

MUSIC_CONTEXT_KEYWORDS = [
    "음악",
    "노래",
    "곡",
    "플레이리스트",
    "듣고",
    "추천",
    "music",
    "song",
    "songs",
    "playlist",
    "track",
    "tracks",
]

NEGATIVE_RECOMMENDATION_PHRASES = [
    "추천은 아니",
    "추천 아니",
    "추천을 원하는 건 아니",
    "추천을 원한 건 아니",
    "듣고 싶은 건 아니",
    "듣고 싶진 않",
]


def _contains_keyword(text: str, keyword: str) -> bool:
    if keyword.isascii() and keyword.replace("-", "").replace("&", "").replace(" ", "").isalnum():
        return re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", text) is not None

    return keyword in text


def _collect_matches(text: str, genre_keywords: dict[str, list[str]]) -> list[tuple[int, str]]:
    matches: list[tuple[int, str]] = []

    for genre, keywords in genre_keywords.items():
        for keyword in keywords:
            normalized_keyword = keyword.lower()

            if not _contains_keyword(text, normalized_keyword):
                continue

            matches.append((text.find(normalized_keyword), genre))
            break

    return matches


def _has_music_context(text: str) -> bool:
    return any(keyword in text for keyword in MUSIC_CONTEXT_KEYWORDS)


def _is_negative_recommendation_context(text: str) -> bool:
    return any(phrase in text for phrase in NEGATIVE_RECOMMENDATION_PHRASES)


def extract_genre(text: str) -> str | None:
    normalized_text = text.lower()

    if _is_negative_recommendation_context(normalized_text):
        return None

    matches = _collect_matches(normalized_text, SAFE_GENRE_KEYWORDS)

    # 일반 단어와 겹칠 수 있는 장르는 음악 관련 문맥이 있을 때만 인정한다.
    if _has_music_context(normalized_text):
        matches.extend(_collect_matches(normalized_text, AMBIGUOUS_GENRE_KEYWORDS))

    if not matches:
        return None

    # 여러 장르가 같이 들어오면 사용자가 먼저 말한 장르를 우선한다.
    return min(matches, key=lambda match: match[0])[1]
