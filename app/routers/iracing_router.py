from fastapi import APIRouter, Request, HTTPException
from app.iracing.endpoints import get_series, get_schedule, get_special_events, get_teams
from jose import jwt, JWTError
from app.config import settings
from app.db.queries import get_iracing_token_for_user

router = APIRouter()


def extract_user_id(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing internal JWT token")

    token = auth.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        return payload.get("user_id")
    except JWTError:
        raise HTTPException(401, "Invalid token")


@router.get("/series")
async def series(request: Request):
    user_id = extract_user_id(request)
    iracing_token = await get_iracing_token_for_user(user_id)
    return await get_series(iracing_token)


@router.get("/series/{season_id}/schedule")
async def schedule(season_id: int, request: Request):
    user_id = extract_user_id(request)
    iracing_token = await get_iracing_token_for_user(user_id)
    return await get_schedule(season_id, iracing_token)


@router.get("/events/special")
async def special(request: Request):
    user_id = extract_user_id(request)
    iracing_token = await get_iracing_token_for_user(user_id)
    return await get_special_events(iracing_token)


@router.get("/teams")
async def teams(request: Request):
    user_id = extract_user_id(request)
    iracing_token = await get_iracing_token_for_user(user_id)
    return await get_teams(iracing_token)