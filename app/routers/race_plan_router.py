"""
Routes for managing Race Plan
"""
from fastapi import APIRouter, HTTPException, Request

from app.models.race_plan import (RacePlanRequest, RacePlanResponse)
from app.db.race_plan_queries import (
    create_race_plan,
    get_race_plan_by_team_and_event,
)
from app.db.queries import get_display_name_from_user_id
from app.db.events_queries import get_event_registration_for_event_and_team, get_registrations_for_event_and_team
from app.db.driver_roster_queries import create_driver_roster_entry_from_event_registration, list_driver_roster_by_race_plan

router = APIRouter(prefix="/race-plan", tags=["race-plan"])

@router.post("/create", response_model=RacePlanResponse)
async def create_race_plan_endpoint(race_plan: RacePlanRequest):
    """Create a new race plan"""
    
    try:
        result = create_race_plan(race_plan)
        event_registrations = get_event_registration_for_event_and_team(race_plan.event_id, race_plan.team_id)
        # Create driver roster entries for each registration
        for registration in event_registrations:
            user_id = registration.user_id
            create_driver_roster_entry_from_event_registration(get_display_name_from_user_id(user_id), result.id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to create race plan: {str(e)}")

@router.get("/list/team/{team_id}/event/{event_id}", response_model=RacePlanResponse)
async def get_race_plan_by_team_and_event_endpoint(team_id: int, event_id: int):
    """Get one race plan for a specific team and event"""

    try:
        result = get_race_plan_by_team_and_event(team_id=team_id, event_id=event_id)
        event_registration = get_event_registration_for_event_and_team(event_id, team_id)
        driver_roster = list_driver_roster_by_race_plan(result.id)

        roster_user_ids = {
            driver.user_id
            for driver in driver_roster
            if driver.user_id is not None
        }

        for registration in event_registration:
            user_id = registration.user_id

            if user_id not in roster_user_ids:
                create_driver_roster_entry_from_event_registration(
                    get_display_name_from_user_id(user_id),
                    result.id,
                    user_id
                )
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to get race plan: {str(e)}")
