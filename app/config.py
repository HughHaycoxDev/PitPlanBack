import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- Config ---
    CLIENT_ID = os.getenv("IRACING_CLIENT_ID")
    CLIENT_SECRET = os.getenv("IRACING_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("IRACING_REDIRECT_URI")
    AUTH_URL = "https://oauth.iracing.com/oauth2/authorize"
    TOKEN_URL = "https://oauth.iracing.com/oauth2/token"
    USERINFO_URL = "https://members-ng.iracing.com/data/member/info"
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    ALGORITHM = "HS256"


settings = Settings()
