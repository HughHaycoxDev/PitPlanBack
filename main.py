from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
import httpx
from datetime import datetime, timedelta
from jose import jwt


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/auth/callback")
async def auth_callback(code: str):
    # Exchange the code for an access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Token request failed")
    token_data = token_resp.json()
    access_token = token_data.get("access_token")

    # Get user info from iRacing
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
        )

    if user_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info")

    user_info = user_resp.json()

    # Create out own JWT for session persistence
    expires = datetime.utcnow() + timedelta(hours=1)
    jwt_token = jwt.encode(
        {"sub": user_info["display_name"], "exp": expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    # Redirect to frontend with token in query
    return RedirectResponse(f"http://localhost:3000/?token={jwt_token}")
