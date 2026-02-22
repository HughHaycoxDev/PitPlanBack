"""
Routes for managing Race Plan
"""
from fastapi import APIRouter, HTTPException, Request

from app.models.race_plan import (RacePlan)
from app.db.race_plan_queries import (
    create_race_plan,
    get_race_plan,
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

@router.get("/list/team/{team_id}/event/{event_id}", response_model=RacePlan)
async def list_race_plan_by_team_and_event_endpoint(team_id: int, event_id: int):
    """Get one race plan for a specific team and event"""

    try:
        result = get_race_plan(team_id=team_id, event_id=event_id)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to get race plan: {str(e)}")
