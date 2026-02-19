"""
Database models for Race Plan
"""
from pydantic import BaseModel

class RacePlan(BaseModel):
    """Model for a race plan"""
    team_id: int