import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# 로컬 개발에서는 API 키를 코드에 직접 쓰지 않고 backend/.env에서 읽는다.
load_dotenv(ENV_PATH)

# 키가 없어도 서버는 켜지게 두고, YouTube 호출 단계에서 임시 데이터로 대체한다.
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
