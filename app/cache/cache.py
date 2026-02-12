import json
from datetime import datetime, timedelta
from .db import get_db


def get_cache(key: str):
    db = get_db()
    row = db.execute(
        "SELECT value, expires_at FROM cache WHERE key=?", (key,)).fetchone()

    if not row:
        return None

    if datetime.utcnow() > datetime.fromisoformat(row["expires_at"]):
        return None

    return json.loads(row["value"])


def set_cache(key: str, value, ttl_hours: int):
    expires = datetime.utcnow() + timedelta(hours=ttl_hours)
    db = get_db()
    db.execute("REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
               (key, json.dumps(value), expires.isoformat())
               )
    db.commit()


def save_iracing_token(user_id, display_name, access, refresh, expires):
    db = get_db()
    db.execute(
        """
        INSERT INTO users (user_id, display_name, iracing_access_token, iracing_refresh_token, token_expires)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            display_name = excluded.display_name,
            iracing_access_token = excluded.iracing_access_token,
            iracing_refresh_token = excluded.iracing_refresh_token,
            token_expires = excluded.token_expires
        """,
        (user_id, display_name, access, refresh, expires)
    )
    db.commit()
