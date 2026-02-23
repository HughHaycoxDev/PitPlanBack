"""
Routes for managing Driver Roster
"""
from fastapi import APIRouter, HTTPException, Request

from app.models.driver_roster import (DriverRoster)
from app.db.driver_roster_queries import (
    delete_driver_roster_entry,
    list_driver_roster_by_race_plan,
    update_driver_roster_entry,
)

router = APIRouter(prefix="/driver-roster", tags=["driver-roster"])

@router.get("/list-by-race-plan/{race_plan_id}", response_model=list[DriverRoster])
async def list_driver_roster_by_race_plan_endpoint(race_plan_id: int):
    """List all driver roster entries for a specific race plan"""
    
    try:
        result = list_driver_roster_by_race_plan(race_plan_id=race_plan_id)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to list driver roster: {str(e)}")
    
@router.put("/update/driver", response_model=DriverRoster)
async def update_driver_roster_by_race_plan_endpoint(driver_roster: DriverRoster):
    """Update driver on driver roster"""
    
    try:
        result = update_driver_roster_entry(driver_roster=driver_roster)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to update driver roster: {str(e)}")
    
@router.delete("/delete/driver/{driver_id}")
async def delete_driver_roster_endpoint(driver_id: int):
    """Delete a driver roster entry"""
    try:
        result = delete_driver_roster_entry(driver_id=driver_id)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to delete driver roster: {str(e)}")