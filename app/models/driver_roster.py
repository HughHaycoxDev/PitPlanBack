"""
Database models for Driver Roster
"""
from pydantic import BaseModel

class DriverRoster(BaseModel):
    """Model for a driver roster entry"""
    id: int | None = None
    color: str
    name: str
    stints: int
    fair_share: bool
    gmt_offset: int
    i_rating: float
    lap_time: float
    factor: int
    preference: str
    race_plan_id: int