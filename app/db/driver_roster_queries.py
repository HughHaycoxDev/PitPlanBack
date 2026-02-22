"""
Database queries for Driver Roster
"""
from app.cache.db import get_db
from app.models.driver_roster import (
    DriverRoster
)
from typing import List

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
               
        FOREIGN KEY (race_plan_id) REFERENCES race_plans(id) ON DELETE CASCADE
    )""")

    db.commit()

def list_driver_roster_by_race_plan(race_plan_id: int) -> List[DriverRoster]:
    """List all driver roster entries for a specific race plan"""
    db = get_db()

    rows = db.execute("""
        SELECT id, color, name, stints, fair_share, gmt_offset, i_rating, lap_time, factor, preference
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
        )
        for row in rows
    ]