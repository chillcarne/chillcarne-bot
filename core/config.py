import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", None)
LOCAL_API_URL = os.getenv("LOCAL_API_URL", None)
REQUIRED_CHANNEL_USERNAME = os.getenv("REQUIRED_CHANNEL_USERNAME", "chillcarne")  # @chillcarne
DEVELOPER_CHAT_ID = int(os.getenv("DEVELOPER_CHAT_ID", "0")) 

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", None)  # например, "bot.log" или путь

TIMEZONE = os.getenv("TIMEZONE", "UTC")