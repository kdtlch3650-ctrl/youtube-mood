KOTE_MOOD_TAGS: dict[str, list[str]] = {
    "힘듦/지침": ["soft", "quiet", "warm"],
    "불안/걱정": ["soft", "quiet", "warm"],
    "슬픔": ["warm", "soft", "late night"],
    "서러움": ["warm", "soft"],
    "절망": ["warm", "quiet"],
    "화남/분노": ["heavy", "uplifting"],
    "짜증": ["heavy", "uplifting"],
    "행복": ["uplifting", "light"],
    "기쁨": ["uplifting", "light"],
    "즐거움/신남": ["uplifting", "light"],
    "기대감": ["uplifting", "light"],
    "편안/쾌적": ["soft", "quiet"],
    "안심/신뢰": ["warm", "soft"],
}

LEGACY_MOOD_TAGS: dict[str, list[str]] = {
    "tired": ["soft", "quiet", "warm"],
    "anxious": ["soft", "quiet", "warm"],
    "sad": ["warm", "soft"],
    "angry": ["heavy", "uplifting"],
    "stressed": ["heavy", "uplifting"],
    "happy": ["uplifting", "light"],
    "hopeful": ["uplifting", "light"],
    "calm": ["soft", "quiet"],
    "focused": ["minimal", "quiet"],
    "lonely": ["late night", "warm", "soft"],
}

SEARCH_KEYWORDS_BY_MOOD: dict[str, str] = {
    "soft": "soft emotional music",
    "quiet": "quiet calm playlist",
    "warm": "warm comfort music",
    "late night": "late night emotional playlist",
    "heavy": "heavy cathartic music",
    "uplifting": "uplifting mood music",
    "light": "light feel good music",
    "minimal": "minimal focus music",
}


def unique_values(values: list[str]) -> list[str]:
    result = []

    for value in values:
        if value not in result:
            result.append(value)

    return result


def build_mood_tags(emotions: list[str]) -> list[str]:
    mood_tags = []

    for emotion in emotions:
        mood_tags.extend(KOTE_MOOD_TAGS.get(emotion, []))
        mood_tags.extend(LEGACY_MOOD_TAGS.get(emotion, []))

    return unique_values(mood_tags)[:4]


def build_search_keywords(emotions: list[str], mood_tags: list[str]) -> list[str]:
    keywords = []

    for mood_tag in mood_tags:
        keyword = SEARCH_KEYWORDS_BY_MOOD.get(mood_tag)

        if keyword:
            keywords.append(keyword)

    # KOTE 라벨 자체가 검색에 도움 되는 경우를 대비해 마지막 후보로 감정 기반 검색어를 추가한다.
    for emotion in emotions:
        keywords.append(f"{emotion} mood music")

    if not keywords:
        keywords.append("relaxing music playlist")

    return unique_values(keywords)[:3]
