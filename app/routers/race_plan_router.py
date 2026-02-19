"""
Routes for managing Race Plan
"""
from fastapi import APIRouter, HTTPException, Request

from app.models.race_plan import (RacePlan)
from app.db.race_plan_queries import (
    create_race_plan
)

router = APIRouter(prefix="/race-plan", tags=["race-plan"])

@router.post("/create", response_model=RacePlan)
async def create_race_plan_endpoint(race_plan: RacePlan):
    """Create a new race plan"""
    
    try:
        result = create_race_plan(race_plan)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to create race plan: {str(e)}")
