from app.db.events_queries import upsert_teams
from .client import iracing_get
from app.cache.cache import get_cache, set_cache
from app.config import settings

SERIES_URL = "https://members-ng.iracing.com/data/series/seasons"
SCHEDULE_URL = "https://members-ng.iracing.com/data/series/schedule"
EVENTS_URL = "https://members-ng.iracing.com/data/special_events/list"
TEAMS_URL = "https://members-ng.iracing.com/data/team/membership"

async def cached_call(key: str, url: str, token: str, ttl_hours=24*7):
    cached = get_cache(key)
    if cached:
        return cached

    data = await iracing_get(url, token)
    set_cache(key, data, ttl_hours)
    return data


async def get_series(token: str):
    return await cached_call("series", SERIES_URL, token)


async def get_schedule(season_id: int, token: str):
    url = f"{SCHEDULE_URL}?season_id={season_id}"
    return await cached_call(f"schedule_{season_id}", url, token)


async def get_special_events(token: str):
    return await cached_call("special_events", EVENTS_URL, token)


async def get_teams(token: str):
    try:
        teams_data = await cached_call("teams", TEAMS_URL, token)
        processed_teams = []
        if isinstance(teams_data, list):
            for team in teams_data:
                processed_teams.append({
                    'team_id': team.get('team_id'),
                    'team_name': team.get('team_name'),
                    'owner': team.get('owner'),
                    'admin': team.get('admin'),
                })
        if processed_teams:
            upsert_teams(processed_teams)

    except Exception as e:
        print(f"Error syncing teams from iRacing API: {str(e)}")
        raise

    return await cached_call("teams", TEAMS_URL, token)
