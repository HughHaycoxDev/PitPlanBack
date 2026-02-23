"""
Database queries for Driver Roster
"""
from app.cache.db import get_db
from app.models.driver_roster import (
    DriverRoster
)
from typing import List

from app.models.events import EventRegistrationDetail

def init_driver_roster_db():
    """Initialize the database with the necessary tables"""
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS driver_rosters (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        color TEXT,
        name TEXT,
        stints INTEGER,
        fair_share BOOLEAN,
        gmt_offset INTEGER,
        i_rating REAL,
        lap_time REAL,
        factor INTEGER,
        preference TEXT,
        race_plan_id INTEGER NOT NULL,
        user_id INTEGER,
               
        FOREIGN KEY (race_plan_id) REFERENCES race_plans(id) ON DELETE CASCADE
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""")

    db.commit()

def list_driver_roster_by_race_plan(race_plan_id: int) -> List[DriverRoster]:
    """List all driver roster entries for a specific race plan"""
    db = get_db()

    rows = db.execute("""
        SELECT id, color, name, stints, fair_share, gmt_offset, i_rating, lap_time, factor, preference, race_plan_id, user_id
        FROM driver_rosters
        WHERE race_plan_id = ?
        """, (race_plan_id,)).fetchall()
    
    return [
        DriverRoster(
            id=row[0],
            color=row[1],
            name=row[2],
            stints=row[3],
            fair_share=bool(row[4]),
            gmt_offset=row[5],
            i_rating=row[6],
            lap_time=row[7],
            factor=row[8],
            preference=row[9],
            race_plan_id=row[10],
            user_id=row[11]
        )
        for row in rows
    ]

def create_driver_roster_entry(race_plan_id: int):
    """Create a driver roster entry"""

    db = get_db()
    db.execute("""
    INSERT INTO driver_rosters (id, color, name, stints, fair_share, gmt_offset, i_rating, lap_time, factor, preference, race_plan_id, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (None, None, None, None, None, None, None, None, None, None, race_plan_id, None))

    db.commit()

def update_driver_roster_entry(driver_roster: DriverRoster) -> DriverRoster:
    """Update a driver roster entry"""
    db = get_db()

    db.execute("""
        UPDATE driver_rosters
        SET color = ?, name = ?, stints = ?, fair_share = ?, gmt_offset = ?, i_rating = ?, lap_time = ?, factor = ?, preference = ?
        WHERE id = ?
    """, (
        driver_roster.color,
        driver_roster.name,
        driver_roster.stints,
        driver_roster.fair_share,
        driver_roster.gmt_offset,
        driver_roster.i_rating,
        driver_roster.lap_time,
        driver_roster.factor,
        driver_roster.preference,
        driver_roster.id
    ))

    db.commit()

    return driver_roster

def delete_driver_roster_entry(driver_id: int):
    """Delete a driver roster entry"""
    db = get_db()

    db.execute("""
        DELETE FROM driver_rosters
        WHERE id = ?
    """, (driver_id,))

    db.commit()

def create_driver_roster_entry_from_event_registration(display_name: str, race_plan_id: int, user_id: int | None = None):
    """Create a driver roster entry from an event registration"""

    db = get_db()
    db.execute("""
    INSERT INTO driver_rosters (id, color, name, stints, fair_share, gmt_offset, i_rating, lap_time, factor, preference, race_plan_id, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (None, None, display_name, None, None, None, None, None, None, None, race_plan_id, user_id))

    db.commit()