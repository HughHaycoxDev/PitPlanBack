import httpx
from app.config import settings
from app.utils.masking import mask_client_secret


async def refresh_iracing_token(refresh_token: str):
    masked_secret = mask_client_secret(
        settings.CLIENT_ID, settings.CLIENT_SECRET)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            settings.TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": settings.CLIENT_ID,
                "client_secret": masked_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    if resp.status_code != 200:
        raise Exception("Failed to refresh token: " + resp.text)

    return resp.json()
