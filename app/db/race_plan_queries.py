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
        time_slot TEXT NOT NULL
    )
    """)

    db.commit()

def create_race_plan(plan: RacePlan) -> RacePlan:
    """Create a new race plan"""
    db = get_db()

    db.execute("""
    INSERT INTO race_plans (id, team_id, car_id, time_slot)
    VALUES (?, ?, ?, ?)
    """, (None, plan.team_id, plan.car_id, plan.time_slot))

    db.commit()
    return plan

def get_race_plans() -> List[RacePlan]:
    """Get all race plans"""
    db = get_db()

    rows = db.execute("SELECT id, team_id, car_id, time_slot FROM race_plans").fetchall()
    return [RacePlan(team_id=row[1], car_id=row[2], time_slot=row[3]) for row in rows]