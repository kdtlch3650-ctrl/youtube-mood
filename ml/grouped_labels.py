GROUPED_LABELS: dict[str, list[str]] = {
    "anxiety": ["불안/걱정", "당황/난처", "부담/안_내킴", "초조함"],
    "sadness": ["슬픔", "서러움", "안타까움/실망", "절망", "외로움"],
    "tiredness": ["힘듦/지침", "지긋지긋", "귀찮음"],
    "irritation": ["짜증", "불평/불만", "화남/분노", "억울함"],
    "positive": ["행복", "기쁨", "즐거움/신남", "기대감", "뿌듯함"],
    "comfort": ["편안/쾌적", "안심/신뢰", "고마움", "감동/감탄"],
    "focus": ["몰입", "깨달음", "흥미"],
}


def convert_kote_labels_to_groups(labels: list[str]) -> list[str]:
    grouped = []

    for group_name, source_labels in GROUPED_LABELS.items():
        if any(label in labels for label in source_labels):
            grouped.append(group_name)

    return grouped or ["neutral"]
