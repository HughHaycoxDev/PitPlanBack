import sqlite3
import time
from app.cache.db import get_db
from app.iracing.oauth import refresh_iracing_token
import datetime


async def get_iracing_token_for_user(user_id: int) -> str:
    db = get_db()

    row = db.execute(
        "SELECT iracing_access_token, iracing_refresh_token, token_expires "
        "FROM users WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if not row:
        raise Exception("User not found in database")

    access_token, refresh_token, expires_at = row

    # If still valid, return as-is
    expires_at = datetime.datetime.fromtimestamp(
        expires_at, tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
    now = datetime.datetime.now(datetime.timezone.utc)
    if expires_at > now:
        return access_token

    # EXPIRED → refresh it
    if not refresh_token:
        raise Exception("Token expired and no refresh token available")

    new_token_data = await refresh_iracing_token(refresh_token)

    new_access = new_token_data["access_token"]
    new_refresh = new_token_data.get("refresh_token", refresh_token)
    new_expires = int(time.time() + new_token_data["expires_in"])

    # Save updated tokens
    db.execute(
        """
        UPDATE users
        SET iracing_access_token = ?, iracing_refresh_token = ?, token_expires = ?
        WHERE user_id = ?
        """,
        (new_access, new_refresh, new_expires, user_id)
    )
    db.commit()

    return new_access

def get_display_name_from_user_id(user_id: int) -> str:
    db = get_db()

    row = db.execute("""
        SELECT display_name FROM users WHERE user_id = ?
    """, (user_id,)).fetchone()

    if not row:
        return None
    return row[0]