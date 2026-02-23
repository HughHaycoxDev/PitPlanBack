"""
Database models for Driver Roster
"""
from typing import Optional

from pydantic import BaseModel

class DriverRoster(BaseModel):
    """Model for a driver roster entry"""
    id: int | None = None
    color: Optional[str] = None
    name: str
    stints: Optional[int] = None
    fair_share: Optional[bool] = None
    gmt_offset: Optional[int] = None
    i_rating: Optional[float] = None
    lap_time: Optional[float] = None
    factor: Optional[int] = None
    preference: Optional[str] = None
    race_plan_id: int
    user_id: Optional[int] = None