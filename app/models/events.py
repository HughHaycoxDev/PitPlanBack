"""
Database models for Events, Cars, Tracks, and their relationships.
"""
from pydantic import BaseModel
from typing import List
from datetime import datetime, date


class CarBase(BaseModel):
    car_id: int
    car_name: str
    logo: str
    tank_size: float


class CarDB(CarBase):
    id: int


class TrackBase(BaseModel):
    track_id: int
    track_name: str
    category: str
    config_name: str
    logo: str
    pit_road_speed_limit: int
    small_image: str


class TrackDB(TrackBase):
    id: int


class TimeSlot(BaseModel):
    """Represents a single time slot for an event"""
    slot_time: datetime


class EventBase(BaseModel):
    event_name: str
    event_description: str = None
    start_date: date
    end_date: date
    duration_minutes: int
    track_id: int
    car_ids: List[int]  
    time_slots: List[TimeSlot]


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    event_name: str = None
    event_description: str = None
    start_date: date = None
    end_date: date = None
    duration_minutes: int = None
    track_id: int = None
    car_ids: List[int] = None
    time_slots: List[TimeSlot] = None


class EventResponse(BaseModel):
    id: int
    event_name: str
    event_description: str = None
    start_date: date
    end_date: date
    duration_minutes: int
    track: TrackDB
    cars: List[CarDB]
    time_slots: List[TimeSlot]

    class Config:
        from_attributes = True

# ===== TEAM AND REGISTRATION MODELS =====

class TeamBase(BaseModel):
    team_id: int
    team_name: str
    owner: bool
    admin: bool
    team_logo: str = None


class TeamDB(TeamBase):
    id: int


class EventRegistrationCreate(BaseModel):
    """Model for creating an event registration"""
    event_id: int
    user_id: int
    team_id: int
    time_slot: datetime
    car_id: int


class EventRegistrationResponse(BaseModel):
    """Model for returning registration details"""
    id: int
    event_id: int
    user_id: int
    team_id: int
    time_slot: datetime
    car_id: int
    registered_at: datetime

    class Config:
        from_attributes = True


class EventRegistrationDetail(BaseModel):
    """Model with full event and team details"""
    id: int
    event: EventResponse
    user_id: int
    team: TeamDB
    time_slot: TimeSlot
    car: CarDB
    registered_at: datetime

    class Config:
        from_attributes = True