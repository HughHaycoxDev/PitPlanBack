"""
Database models for Race Plan
"""
from pydantic import BaseModel
from datetime import datetime

class RacePlan(BaseModel):
    """Model for a race plan"""
    team_id: int
    car_id: int
    time_slot: datetime