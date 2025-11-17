from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
import httpx
import base64
import hashlib
import secrets
import urllib
from datetime import datetime, timedelta
from jose import jwt

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Config ---
CLIENT_ID = os.getenv("IRACING_CLIENT_ID")
CLIENT_SECRET = os.getenv("IRACING_CLIENT_SECRET")
REDIRECT_URI = os.getenv("IRACING_REDIRECT_URI")
AUTH_URL = "https://oauth.iracing.com/oauth2/authorize"
TOKEN_URL = "https://oauth.iracing.com/oauth2/token"
USERINFO_URL = "https://members-ng.iracing.com/data/member/info"
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"


# --- PKCE helpers ---
def create_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)).rstrip(b'=').decode()
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(
        code_verifier.encode()).digest()).rstrip(b'=').decode()
    return code_verifier, code_challenge


# --- Mask client secret ---
def mask_client_secret(client_id: str, client_secret: str) -> str:
    normalized_id = client_id.strip().lower()
    hasher = hashlib.sha256()
    hasher.update(f"{client_secret}{normalized_id}".encode("utf-8"))
    return base64.b64encode(hasher.digest()).decode()


# --- Login route ---
@app.get("/login")
def login():
    # Generate PKCE pair
    code_verifier, code_challenge = create_pkce_pair()

 # Encode code_verifier into state
    state = base64.urlsafe_b64encode(code_verifier.encode()).decode()

    auth_url = (
        f"{AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope=iracing.auth"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&state={urllib.parse.quote(state)}"
    )

    return RedirectResponse(auth_url)


# --- Callback route ---
@app.get("/auth/callback")
async def auth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    if error:
        raise HTTPException(400, error)
    if not code:
        raise HTTPException(400, "Missing authorization code")
    if not state:
        raise HTTPException(400, "Missing state parameter")

    # Decode the code_verifier from state
    try:
        code_verifier = base64.urlsafe_b64decode(state.encode()).decode()
    except Exception:
        raise HTTPException(400, "Invalid state parameter")

    # Mask the client secret (per iRacing docs)
    masked_secret = mask_client_secret(CLIENT_ID, CLIENT_SECRET)

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": code_verifier,
                "client_id": CLIENT_ID,
                "client_secret": masked_secret,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

    if token_resp.status_code != 200:
        print("Token exchange failed:", token_resp.text)
        raise HTTPException(400, "Token exchange failed")

    access_token = token_resp.json().get("access_token")
    if not access_token:
        raise HTTPException(400, "No access token received")

    # Fetch user info
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if user_resp.status_code != 200:
        raise HTTPException(400, "User info fetch failed")

    user_info = user_resp.json()

    # Generate internal JWT
    expires = datetime.utcnow() + timedelta(hours=1)
    jwt_token = jwt.encode(
        {"sub": user_info.get("display_name"), "exp": expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    # Redirect to frontend with JWT
    return RedirectResponse(f"http://127.0.0.1:3000/?token={jwt_token}")
