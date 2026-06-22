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

GROUPED_MOOD_TAGS: dict[str, list[str]] = {
    "anxiety": ["soft", "quiet", "warm"],
    "sadness": ["warm", "soft", "late night"],
    "tiredness": ["soft", "quiet", "warm"],
    "irritation": ["heavy", "uplifting"],
    "positive": ["uplifting", "light"],
    "comfort": ["warm", "soft"],
    "focus": ["minimal", "quiet"],
    "neutral": ["soft"],
}

RELATED_MOOD_TAGS: dict[str, list[str]] = {
    "soft": ["quiet", "warm"],
    "quiet": ["soft", "minimal"],
    "warm": ["soft", "light"],
    "late night": ["heavy", "soft"],
    "heavy": ["late night"],
    "uplifting": ["light"],
    "light": ["uplifting", "soft"],
    "minimal": ["quiet"],
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

GENRE_SEARCH_PHRASES_BY_MOOD: dict[str, str] = {
    "soft": "soft",
    "quiet": "quiet calm",
    "warm": "warm comfort",
    "late night": "late night",
    "heavy": "heavy cathartic",
    "uplifting": "uplifting",
    "light": "light feel good",
    "minimal": "minimal focus",
}

TEXT_MOOD_ADJUSTMENTS = [
    {
        "avoid_keywords": ["무거운", "무겁", "어두운", "어둡", "강한", "격한"],
        "negative_words": ["싫", "부담", "피하고", "원하지", "안 듣고"],
        "remove_tags": ["heavy", "late night"],
        "add_tags": ["soft", "light"],
    },
    {
        "avoid_keywords": ["슬픈", "슬프", "우울", "눈물"],
        "negative_words": ["싫", "부담", "피하고", "원하지", "안 듣고"],
        "remove_tags": ["late night"],
        "add_tags": ["warm", "light"],
    },
    {
        "avoid_keywords": ["신나는", "신나", "밝은", "활기찬"],
        "negative_words": ["싫", "부담", "피하고", "원하지", "안 듣고"],
        "remove_tags": ["uplifting", "light"],
        "add_tags": ["soft", "quiet"],
    },
]


def unique_values(values: list[str]) -> list[str]:
    result = []

    for value in values:
        if value not in result:
            result.append(value)

    return result


def expand_related_tags(tags: list[str]) -> list[str]:
    expanded = []

    for tag in tags:
        expanded.append(tag)
        expanded.extend(RELATED_MOOD_TAGS.get(tag, []))

    return unique_values(expanded)


def build_mood_tags(emotions: list[str]) -> list[str]:
    mood_tags = []

    for emotion in emotions:
        mood_tags.extend(GROUPED_MOOD_TAGS.get(emotion, []))
        mood_tags.extend(KOTE_MOOD_TAGS.get(emotion, []))
        mood_tags.extend(LEGACY_MOOD_TAGS.get(emotion, []))

    return unique_values(mood_tags)[:4]


def adjust_mood_tags_by_text(mood_tags: list[str], text: str) -> list[str]:
    adjusted_tags = mood_tags.copy()

    for rule in TEXT_MOOD_ADJUSTMENTS:
        has_avoid_target = any(keyword in text for keyword in rule["avoid_keywords"])
        has_negative_word = any(word in text for word in rule["negative_words"])

        if not has_avoid_target or not has_negative_word:
            continue

        # 사용자가 원하지 않는 분위기를 직접 말한 경우에는 감정 라벨보다 문장 의도를 우선한다.
        filtered_tags = [tag for tag in adjusted_tags if tag not in rule["remove_tags"]]
        adjusted_tags = [*rule["add_tags"], *filtered_tags]

    return unique_values(adjusted_tags)[:4]


def merge_requested_mood_tags(
    mood_tags: list[str],
    preferred_mood_tags: list[str] | None = None,
    avoid_mood_tags: list[str] | None = None,
) -> list[str]:
    preferred = preferred_mood_tags or []
    avoid = set(avoid_mood_tags or [])

    merged_tags = [*preferred, *mood_tags]
    filtered_tags = [tag for tag in merged_tags if tag not in avoid]

    if not filtered_tags:
        filtered_tags = [*preferred, *mood_tags]

    return unique_values(filtered_tags)[:4]


def resolve_mood_tags(
    mood_tags: list[str],
    preferred_mood_tags: list[str] | None = None,
    avoid_mood_tags: list[str] | None = None,
    blocked_mood_tags: list[str] | None = None,
) -> list[str]:
    preferred = preferred_mood_tags or []
    avoid = set(expand_related_tags(avoid_mood_tags or []))
    blocked = set(expand_related_tags(blocked_mood_tags or []))

    merged_tags = [*preferred, *mood_tags]
    filtered_tags = [tag for tag in merged_tags if tag not in avoid and tag not in blocked]

    if not filtered_tags:
        filtered_tags = [*preferred, *mood_tags]

    return unique_values(filtered_tags)[:4]


def build_search_keywords(
    emotions: list[str],
    mood_tags: list[str],
    genre: str | None = None,
    extra_keywords: list[str] | None = None,
) -> list[str]:
    keywords = []

    for keyword in extra_keywords or []:
        keywords.append(keyword)

    if genre:
        for mood_tag in mood_tags:
            phrase = GENRE_SEARCH_PHRASES_BY_MOOD.get(mood_tag)

            if phrase:
                keywords.append(f"{phrase} {genre} music")
                keywords.append(f"{phrase} {genre} playlist")
    else:
        for mood_tag in mood_tags:
            keyword = SEARCH_KEYWORDS_BY_MOOD.get(mood_tag)

            if keyword:
                keywords.append(keyword)

    # KOTE 라벨 자체가 검색에 도움 되는 경우를 대비해 마지막 후보로 감정 기반 검색어를 추가한다.
    for emotion in emotions:
        if genre:
            keywords.append(f"{emotion} {genre} music")
        else:
            keywords.append(f"{emotion} mood music")

    if not keywords:
        fallback_keyword = f"relaxing {genre} music" if genre else "relaxing music playlist"
        keywords.append(fallback_keyword)

    return unique_values(keywords)[:3]
