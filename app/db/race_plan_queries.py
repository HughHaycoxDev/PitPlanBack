"""
Database queries for Race Plan
"""
from app.cache.db import get_db
from app.models.race_plan import (
    RacePlan
)
from typing import List

def init_race_plan_db():
    """Initialize the database with the necessary tables"""
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS race_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL,
        car_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        time_slot TEXT NOT NULL,

        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
        FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE,
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
    )
    """)

    db.commit()

def create_race_plan(plan: RacePlan) -> RacePlan:
    """Create a new race plan"""
    db = get_db()

    db.execute("""
    INSERT INTO race_plans (id, team_id, car_id, time_slot, event_id)
    VALUES (?, ?, ?, ?, ?)
    """, (None, plan.team_id, plan.car_id, plan.time_slot, plan.event_id))

    db.commit()
    return plan

def get_race_plan(team_id: int, event_id: int) -> RacePlan:
    db = get_db()

    row = db.execute("""
        SELECT team_id, car_id, event_id, time_slot
        FROM race_plans
        WHERE team_id=? AND event_id=?
    """, (team_id, event_id)).fetchone()

    if not row:
        raise ValueError("Race plan not found")

    return RacePlan(
        team_id=row[0],
        car_id=row[1],
        event_id=row[2],
        time_slot=row[3]
    )