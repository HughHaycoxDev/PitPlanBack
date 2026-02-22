"""
Database models for Race Plan
"""
from pydantic import BaseModel
from datetime import datetime

class RacePlanRequest(BaseModel):
    """Model for a race plan"""
    team_id: int
    car_id: int
    time_slot: datetime
    event_id: int

class RacePlanResponse(BaseModel):
    """Model for a race plan"""
    id: int
    team_id: int
    car_id: int
    time_slot: datetime
    event_id: int