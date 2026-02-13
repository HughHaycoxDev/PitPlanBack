"""
Routes for managing Events, Cars, and Tracks
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List

from app.models.events import (
    EventCreate, EventUpdate, EventResponse, CarDB, TrackDB
)
from app.db.events_queries import (
    create_event, get_event_by_id, get_all_events, update_event, delete_event,
    get_all_cars, get_car_by_id, get_all_tracks, get_track_by_id, init_events_db
)
from app.iracing.sync import sync_all_iracing_data, sync_cars_from_iracing, sync_tracks_from_iracing
from app.db.queries import get_iracing_token_for_user
from app.config import settings
from jose import jwt, JWTError

router = APIRouter(prefix="/events", tags=["events"])


def extract_user_id(request: Request):
    """Extract user ID from JWT token in Authorization header"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing internal JWT token")

    token = auth.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        return payload.get("user_id")
    except JWTError:
        raise HTTPException(401, "Invalid token")


# ===== SYNC ENDPOINTS =====

@router.post("/sync/cars")
async def sync_cars(request: Request):
    """Sync cars from iRacing API"""
    user_id = extract_user_id(request)
    iracing_token = await get_iracing_token_for_user(user_id)
    
    try:
        cars = await sync_cars_from_iracing(iracing_token)
        return {
            "status": "success",
            "cars_synced": len(cars),
            "message": f"Successfully synced {len(cars)} cars"
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to sync cars: {str(e)}")


@router.post("/sync/tracks")
async def sync_tracks(request: Request):
    """Sync tracks from iRacing API"""
    user_id = extract_user_id(request)
    iracing_token = await get_iracing_token_for_user(user_id)
    
    try:
        tracks = await sync_tracks_from_iracing(iracing_token)
        return {
            "status": "success",
            "tracks_synced": len(tracks),
            "message": f"Successfully synced {len(tracks)} tracks"
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to sync tracks: {str(e)}")


@router.post("/sync/all")
async def sync_all(request: Request):
    """Sync both cars and tracks from iRacing API"""
    user_id = extract_user_id(request)
    iracing_token = await get_iracing_token_for_user(user_id)
    
    result = await sync_all_iracing_data(iracing_token)
    
    if result['status'] == 'error':
        raise HTTPException(500, result.get('message', 'Failed to sync data'))
    
    return {
        "status": "success",
        "cars_synced": len(result['cars']),
        "tracks_synced": len(result['tracks']),
        "message": f"Successfully synced {len(result['cars'])} cars and {len(result['tracks'])} tracks"
    }


# ===== CARS ENDPOINTS =====

@router.get("/cars", response_model=List[CarDB])
async def get_cars(request: Request):
    """Get all cars"""
    extract_user_id(request)  
    return get_all_cars()


@router.get("/cars/{car_id}", response_model=CarDB)
async def get_car(car_id: int, request: Request):
    """Get a specific car by ID"""
    extract_user_id(request)  
    car = get_car_by_id(car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    return car


# ===== TRACKS ENDPOINTS =====

@router.get("/tracks", response_model=List[TrackDB])
async def get_tracks(request: Request):
    """Get all tracks"""
    extract_user_id(request)  
    return get_all_tracks()


@router.get("/tracks/{track_id}", response_model=TrackDB)
async def get_track(track_id: int, request: Request):
    """Get a specific track by ID"""
    extract_user_id(request)  
    track = get_track_by_id(track_id)
    if not track:
        raise HTTPException(404, "Track not found")
    return track


# ===== EVENTS ENDPOINTS =====

@router.post("/", response_model=EventResponse)
async def create_new_event(event: EventCreate, request: Request):
    """Create a new event with time slots and associated cars"""
    extract_user_id(request)  
    
    # Validate track exists
    track = get_track_by_id(event.track_id)
    if not track:
        raise HTTPException(400, f"Track with ID {event.track_id} not found")
    
    # Validate all cars exist
    for car_id in event.car_ids:
        car = get_car_by_id(car_id)
        if not car:
            raise HTTPException(400, f"Car with ID {car_id} not found")
    
    event_id = create_event(event)
    return get_event_by_id(event_id)


@router.get("/", response_model=List[EventResponse])
async def get_events(request: Request):
    """Get all events"""
    extract_user_id(request)  
    return get_all_events()


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, request: Request):
    """Get a specific event by ID"""
    extract_user_id(request)  
    event = get_event_by_id(event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_existing_event(event_id: int, event: EventUpdate, request: Request):
    """Update an existing event"""
    extract_user_id(request)  
    
    # Check if event exists
    existing_event = get_event_by_id(event_id)
    if not existing_event:
        raise HTTPException(404, "Event not found")
    
    # Validate track if provided
    if event.track_id is not None:
        track = get_track_by_id(event.track_id)
        if not track:
            raise HTTPException(400, f"Track with ID {event.track_id} not found")
    
    # Validate all cars if provided
    if event.car_ids is not None:
        for car_id in event.car_ids:
            car = get_car_by_id(car_id)
            if not car:
                raise HTTPException(400, f"Car with ID {car_id} not found")
    
    updated_event = update_event(event_id, event)
    return updated_event


@router.delete("/{event_id}")
async def delete_existing_event(event_id: int, request: Request):
    """Delete an event"""
    extract_user_id(request)  
    
    # Check if event exists
    event = get_event_by_id(event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    
    delete_event(event_id)
    return {"message": "Event deleted successfully"}
