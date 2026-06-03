import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
WECHAT_WEBHOOK_URL = os.getenv("WECHAT_WEBHOOK_URL", "")
TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME", "senka.jpg")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))
ACTIVE_TIME_START = int(os.getenv("ACTIVE_TIME_START", "21"))
ACTIVE_TIME_END = int(os.getenv("ACTIVE_TIME_END", "23"))

RAPIDAPI_HOST = "tiktok-video-no-watermark2.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}"
