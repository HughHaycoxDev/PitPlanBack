from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers= ["*"],
)

# Config
CLIENT_ID = os.getenv("IRACING_CLIENT_ID")
CLIENT_SECRET = os.getenv("IRACING_CLIENT_SECRET")
REDIRECT_URI = os.getenv("IRACING_REDIRECT_URI")
AUTH_URL = os.getenv("IRACING_AUTH_URL")
TOKEN_URL = os.getenv("IRACING_TOKEN_URL")
USERINFO_URL = os.getenv("IRACING_USERINFO_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

# Login and callback routes

@app.get("/login")
def login():
    # Redirect user to iracing OAuth2 consent screen
    redirect_uri = (
        f"{AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid profile"
    )
    return RedirectResponse(redirect_uri)

    
#ToDo callback route