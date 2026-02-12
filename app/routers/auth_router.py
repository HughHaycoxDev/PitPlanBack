from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
import base64
from datetime import datetime, timedelta
from jose import jwt

from app.oauth.iracing_oauth import build_login_redirect, exchange_code_for_token
from app.config import settings
from app.iracing.client import iracing_get
from app.cache.cache import save_iracing_token

router = APIRouter()

# --- Login route ---


@router.get("/login")
def login():
    url, state = build_login_redirect()
    return RedirectResponse(url)

# --- Callback route ---


@router.get("/auth/callback")
async def auth_callback(code: str = None, state: str = None):
    if not code or not state:
        raise HTTPException(400, "Missing parameters")

    code_verifier = base64.urlsafe_b64decode(state.encode()).decode()

    token_data = await exchange_code_for_token(code, code_verifier)
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in")

    if not access_token:
        raise HTTPException(400, "No access token received")

    # Fetch user info
    user_info = await iracing_get(settings.USERINFO_URL, access_token)

    user_id = user_info.get("cust_id")
    display_name = user_info.get("display_name")

    if not user_id:
        raise HTTPException(400, "No user ID in iRacing user info")

    expires_at = int(
        (datetime.utcnow() + timedelta(seconds=expires_in)).timestamp())

    save_iracing_token(
        user_id=user_id,
        display_name=display_name,
        access=access_token,
        refresh=refresh_token,
        expires=expires_at
    )

    payload = {
        "sub": display_name,
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    # Generate internal JWT
    jwt_token = jwt.encode(payload, settings.SECRET_KEY,
                           algorithm=settings.ALGORITHM)

    # Redirect to frontend with JWT
    return RedirectResponse(f"http://127.0.0.1:3000/?token={jwt_token}")
