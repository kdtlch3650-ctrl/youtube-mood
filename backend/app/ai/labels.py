# 감정 태그는 "사용자가 지금 어떤 상태인지"를 나타낸다.
# 한글 뜻을 같이 적어두면 나중에 데이터 확인할 때 이해하기 쉽다.
EMOTION_LABELS: dict[str, str] = {
    "calm": "차분함",
    "tired": "지침",
    "sad": "슬픔",
    "anxious": "불안함",
    "focused": "집중함",
    "stressed": "스트레스",
    "angry": "화남",
    "lonely": "외로움",
    "hopeful": "기대감",
    "happy": "기쁨",
}

# 분위기 태그는 "어떤 음악 느낌이 어울리는지"를 나타낸다.
MOOD_LABELS: dict[str, str] = {
    "soft": "부드러운",
    "warm": "따뜻한",
    "light": "가벼운",
    "heavy": "무거운",
    "quiet": "조용한",
    "dreamy": "몽환적인",
    "uplifting": "기분이 올라가는",
    "minimal": "미니멀한",
    "late night": "늦은 밤",
    "acoustic": "어쿠스틱한",
}

