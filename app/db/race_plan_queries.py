"""
Database queries for Race Plan
"""
from app.cache.db import get_db
from app.models.race_plan import (
    RacePlan
)

def init_race_plan_db():
    """Initialize the database with the necessary tables"""
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS race_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL
    )
    """)

    print(db)

    db.commit()

def create_race_plan(plan: RacePlan) -> RacePlan:
    """Create a new race plan"""
    db = get_db()

    db.execute("""
    INSERT INTO race_plans (id, team_id)
    VALUES (?, ?)
    """, (None, plan.team_id))

    db.commit()
    return plan