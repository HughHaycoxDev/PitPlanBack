import base64
import urllib
import httpx
from fastapi import HTTPException
from app.utils.pkce import create_pkce_pair
from app.utils.masking import mask_client_secret
from app.config import settings


def build_login_redirect():
    # Generate PKCE pair
    code_verifier, code_challenge = create_pkce_pair()

    # Encode code_verifier into state
    state = base64.urlsafe_b64encode(code_verifier.encode()).decode()

    auth_url = (
        f"{settings.AUTH_URL}?response_type=code"
        f"&client_id={settings.CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(settings.REDIRECT_URI)}"
        f"&scope=iracing.auth"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&state={urllib.parse.quote(state)}"
    )

    return auth_url, state


async def exchange_code_for_token(code: str, code_verifier: str):
    # Mask the client secret (per iRacing docs)
    masked_secret = mask_client_secret(
        settings.CLIENT_ID, settings.CLIENT_SECRET)

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            settings.TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.REDIRECT_URI,
                "code_verifier": code_verifier,
                "client_id": settings.CLIENT_ID,
                "client_secret": masked_secret,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

    if token_resp.status_code != 200:
        print("Token exchange failed:", token_resp.text)
        raise HTTPException(400, "Token exchange failed")

    return token_resp.json()
