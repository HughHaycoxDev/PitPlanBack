"""
Database queries for Events, Tracks, Cars, Teams, and Registrations
"""
import sqlite3
import json
from datetime import datetime, date
from typing import List, Optional
from app.cache.db import get_db
from app.db.queries import get_display_name_from_user_id
from app.models.events import (
    EventCreate, EventUpdate, EventResponse, TrackDB, CarDB, TimeSlot,
    EventRegistrationCreate, EventRegistrationResponse, EventRegistrationDetail,
    TeamBase, TeamDB
)


def init_events_db():
    """Initialize the events-related tables"""
    db = get_db()
    
    # Cars table
    db.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER UNIQUE NOT NULL,
        car_name TEXT NOT NULL,
        logo TEXT,
        tank_size REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tracks table
    db.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id INTEGER UNIQUE NOT NULL,
        track_name TEXT NOT NULL,
        category TEXT,
        config_name TEXT,
        logo TEXT,
        pit_road_speed_limit INTEGER,
        small_image TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Events table
    db.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT NOT NULL,
        event_description TEXT,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        duration_minutes INTEGER NOT NULL,
        track_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (track_id) REFERENCES tracks(id)
    )
    """)
    
    # Time slots table
    db.execute("""
    CREATE TABLE IF NOT EXISTS event_time_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        slot_time DATETIME NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
    )
    """)
    
    # Junction table for many-to-many relationship between events and cars
    db.execute("""
    CREATE TABLE IF NOT EXISTS event_cars (
        event_id INTEGER NOT NULL,
        car_id INTEGER NOT NULL,
        PRIMARY KEY (event_id, car_id),
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
        FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
    )
    """)
    
    # Teams table
    db.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER UNIQUE NOT NULL,
        team_name TEXT NOT NULL,
        owner INTEGER NOT NULL,
        admin INTEGER NOT NULL,
        team_logo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Event registrations table - stores user registrations for events
    db.execute("""
    CREATE TABLE IF NOT EXISTS event_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL,
        time_slot DATETIME NOT NULL,
        car_id INTEGER NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (event_id, user_id, team_id),
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
        FOREIGN KEY (time_slot) REFERENCES event_time_slots(slot_time) ON DELETE CASCADE,
        FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
    )
    """)
    
    db.commit()


# ===== CAR QUERIES =====

def upsert_cars(cars_data: List[dict]) -> None:
    """Insert or update multiple cars from iRacing API data"""
    db = get_db()
    
    for car in cars_data:
        db.execute("""
        INSERT INTO cars (car_id, car_name, logo, tank_size, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(car_id) DO UPDATE SET
            car_name = excluded.car_name,
            logo = excluded.logo,
            tank_size = excluded.tank_size,
            updated_at = CURRENT_TIMESTAMP
        """, (
            car.get('car_id'),
            car.get('car_name'),
            car.get('logo'),
            car.get('tank_size')
        ))
    
    db.commit()


def get_all_cars() -> List[CarDB]:
    """Get all cars from database"""
    db = get_db()
    rows = db.execute("SELECT id, car_id, car_name, logo, tank_size FROM cars ORDER BY car_name").fetchall()
    return [CarDB(
        id=row[0],
        car_id=row[1],
        car_name=row[2],
        logo=row[3],
        tank_size=row[4]
    ) for row in rows]


def get_car_by_id(car_id: int) -> Optional[CarDB]:
    """Get a single car by ID"""
    db = get_db()
    row = db.execute("SELECT id, car_id, car_name, logo, tank_size FROM cars WHERE id = ?", (car_id,)).fetchone()
    if not row:
        return None
    return CarDB(
        id=row[0],
        car_id=row[1],
        car_name=row[2],
        logo=row[3],
        tank_size=row[4]
    )


# ===== TRACK QUERIES =====

def upsert_tracks(tracks_data: List[dict]) -> None:
    """Insert or update multiple tracks from iRacing API data"""
    db = get_db()
    
    for track in tracks_data:
        db.execute("""
        INSERT INTO tracks (track_id, track_name, category, config_name, logo, pit_road_speed_limit, small_image, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(track_id) DO UPDATE SET
            track_name = excluded.track_name,
            category = excluded.category,
            config_name = excluded.config_name,
            logo = excluded.logo,
            pit_road_speed_limit = excluded.pit_road_speed_limit,
            small_image = excluded.small_image,
            updated_at = CURRENT_TIMESTAMP
        """, (
            track.get('track_id'),
            track.get('track_name'),
            track.get('category'),
            track.get('config_name'),
            track.get('logo'),
            track.get('pit_road_speed_limit'),
            track.get('small_image')
        ))
    
    db.commit()


def get_all_tracks() -> List[TrackDB]:
    """Get all tracks from database"""
    db = get_db()
    rows = db.execute("""
        SELECT id, track_id, track_name, category, config_name, logo, pit_road_speed_limit, small_image 
        FROM tracks ORDER BY track_name
    """).fetchall()
    return [TrackDB(
        id=row[0],
        track_id=row[1],
        track_name=row[2],
        category=row[3],
        config_name=row[4],
        logo=row[5],
        pit_road_speed_limit=row[6],
        small_image=row[7]
    ) for row in rows]


def get_track_by_id(track_id: int) -> Optional[TrackDB]:
    """Get a single track by ID"""
    db = get_db()
    row = db.execute("""
        SELECT id, track_id, track_name, category, config_name, logo, pit_road_speed_limit, small_image 
        FROM tracks WHERE id = ?
    """, (track_id,)).fetchone()
    if not row:
        return None
    return TrackDB(
        id=row[0],
        track_id=row[1],
        track_name=row[2],
        category=row[3],
        config_name=row[4],
        logo=row[5],
        pit_road_speed_limit=row[6],
        small_image=row[7]
    )


# ===== EVENT QUERIES =====

def create_event(event_data: EventCreate) -> int:
    """Create a new event and return its ID"""
    db = get_db()
    
    # Insert the event
    cursor = db.execute("""
        INSERT INTO events (event_name, event_description, start_date, end_date, duration_minutes, track_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        event_data.event_name,
        event_data.event_description,
        event_data.start_date,
        event_data.end_date,
        event_data.duration_minutes,
        event_data.track_id
    ))
    
    event_id = cursor.lastrowid
    
    # Insert time slots
    for slot in event_data.time_slots:
        db.execute("""
            INSERT INTO event_time_slots (event_id, slot_time)
            VALUES (?, ?)
        """, (event_id, slot.slot_time))
    
    # Insert car associations
    for car_id in event_data.car_ids:
        db.execute("""
            INSERT INTO event_cars (event_id, car_id)
            VALUES (?, ?)
        """, (event_id, car_id))
    
    db.commit()
    return event_id


def get_event_by_id(event_id: int) -> Optional[EventResponse]:
    """Get a single event by ID with all relationships"""
    db = get_db()
    
    # Get event
    event_row = db.execute("""
        SELECT e.id, e.event_name, e.event_description, e.start_date, e.end_date, e.duration_minutes, e.track_id
        FROM events e
        WHERE e.id = ?
    """, (event_id,)).fetchone()
    
    if not event_row:
        return None
    
    # Get track
    track_row = db.execute("""
        SELECT id, track_id, track_name, category, config_name, logo, pit_road_speed_limit, small_image
        FROM tracks WHERE id = ?
    """, (event_row[6],)).fetchone()
    
    track = TrackDB(
        id=track_row[0],
        track_id=track_row[1],
        track_name=track_row[2],
        category=track_row[3],
        config_name=track_row[4],
        logo=track_row[5],
        pit_road_speed_limit=track_row[6],
        small_image=track_row[7]
    ) if track_row else None
    
    # Get cars
    car_rows = db.execute("""
        SELECT c.id, c.car_id, c.car_name, c.logo, c.tank_size
        FROM cars c
        JOIN event_cars ec ON c.id = ec.car_id
        WHERE ec.event_id = ?
    """, (event_id,)).fetchall()
    
    cars = [CarDB(
        id=row[0],
        car_id=row[1],
        car_name=row[2],
        logo=row[3],
        tank_size=row[4]
    ) for row in car_rows]
    
    # Get time slots
    slot_rows = db.execute("""
        SELECT slot_time FROM event_time_slots
        WHERE event_id = ?
        ORDER BY slot_time
    """, (event_id,)).fetchall()
    
    time_slots = [TimeSlot(slot_time=datetime.fromisoformat(row[0])) for row in slot_rows]
    
    return EventResponse(
        id=event_row[0],
        event_name=event_row[1],
        event_description=event_row[2],
        start_date=event_row[3],
        end_date=event_row[4],
        duration_minutes=event_row[5],
        track=track,
        cars=cars,
        time_slots=time_slots
    )


def get_all_events() -> List[EventResponse]:
    """Get all events with all relationships"""
    db = get_db()
    
    event_rows = db.execute("""
        SELECT id, event_name, event_description, start_date, end_date, duration_minutes, track_id
        FROM events
        ORDER BY start_date DESC
    """).fetchall()
    
    events = []
    for event_row in event_rows:
        event_id = event_row[0]
        
        # Get track
        track_row = db.execute("""
            SELECT id, track_id, track_name, category, config_name, logo, pit_road_speed_limit, small_image
            FROM tracks WHERE id = ?
        """, (event_row[6],)).fetchone()
        
        track = TrackDB(
            id=track_row[0],
            track_id=track_row[1],
            track_name=track_row[2],
            category=track_row[3],
            config_name=track_row[4],
            logo=track_row[5],
            pit_road_speed_limit=track_row[6],
            small_image=track_row[7]
        ) if track_row else None
        
        # Get cars
        car_rows = db.execute("""
            SELECT c.id, c.car_id, c.car_name, c.logo, c.tank_size
            FROM cars c
            JOIN event_cars ec ON c.id = ec.car_id
            WHERE ec.event_id = ?
        """, (event_id,)).fetchall()
        
        cars = [CarDB(
            id=row[0],
            car_id=row[1],
            car_name=row[2],
            logo=row[3],
            tank_size=row[4]
        ) for row in car_rows]
        
        # Get time slots
        slot_rows = db.execute("""
            SELECT slot_time FROM event_time_slots
            WHERE event_id = ?
            ORDER BY slot_time
        """, (event_id,)).fetchall()
        
        time_slots = [TimeSlot(slot_time=datetime.fromisoformat(row[0])) for row in slot_rows]
        
        events.append(EventResponse(
            id=event_row[0],
            event_name=event_row[1],
            event_description=event_row[2],
            start_date=event_row[3],
            end_date=event_row[4],
            duration_minutes=event_row[5],
            track=track,
            cars=cars,
            time_slots=time_slots
        ))
    
    return events


def update_event(event_id: int, event_data: EventUpdate) -> Optional[EventResponse]:
    """Update an existing event"""
    db = get_db()
    
    # Check if event exists
    existing = db.execute("SELECT id FROM events WHERE id = ?", (event_id,)).fetchone()
    if not existing:
        return None
    
    # Update event fields
    updates = []
    params = []
    
    if event_data.event_name is not None:
        updates.append("event_name = ?")
        params.append(event_data.event_name)
    if event_data.event_description is not None:
        updates.append("event_description = ?")
        params.append(event_data.event_description)
    if event_data.start_date is not None:
        updates.append("start_date = ?")
        params.append(event_data.start_date)
    if event_data.end_date is not None:
        updates.append("end_date = ?")
        params.append(event_data.end_date)
    if event_data.duration_minutes is not None:
        updates.append("duration_minutes = ?")
        params.append(event_data.duration_minutes)
    if event_data.track_id is not None:
        updates.append("track_id = ?")
        params.append(event_data.track_id)
    
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE events SET {', '.join(updates)} WHERE id = ?"
        params.append(event_id)
        db.execute(query, params)
    
    # Update time slots if provided
    if event_data.time_slots is not None:
        db.execute("DELETE FROM event_time_slots WHERE event_id = ?", (event_id,))
        for slot in event_data.time_slots:
            db.execute("""
                INSERT INTO event_time_slots (event_id, slot_time)
                VALUES (?, ?)
            """, (event_id, slot.slot_time))
    
    # Update cars if provided
    if event_data.car_ids is not None:
        db.execute("DELETE FROM event_cars WHERE event_id = ?", (event_id,))
        for car_id in event_data.car_ids:
            db.execute("""
                INSERT INTO event_cars (event_id, car_id)
                VALUES (?, ?)
            """, (event_id, car_id))
    
    db.commit()
    return get_event_by_id(event_id)


def delete_event(event_id: int) -> bool:
    """Delete an event and all its relationships"""
    db = get_db()
    
    # Check if event exists
    existing = db.execute("SELECT id FROM events WHERE id = ?", (event_id,)).fetchone()
    if not existing:
        return False
    
    # Delete time slots (will cascade)
    db.execute("DELETE FROM event_time_slots WHERE event_id = ?", (event_id,))
    
    # Delete event cars (will cascade)
    db.execute("DELETE FROM event_cars WHERE event_id = ?", (event_id,))
    
    # Delete event
    db.execute("DELETE FROM events WHERE id = ?", (event_id,))
    
    db.commit()
    return True

# ===== TEAM QUERIES =====

def upsert_teams(teams_data: List[dict]) -> None:
    """Insert or update multiple teams from iRacing API data"""
    db = get_db()
    
    for team in teams_data:
        db.execute("""
        INSERT INTO teams (team_id, team_name, owner, admin, team_logo, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(team_id) DO UPDATE SET
            team_name = excluded.team_name,
            owner = excluded.owner,
            admin = excluded.admin,
            team_logo = excluded.team_logo,
            updated_at = CURRENT_TIMESTAMP
        """, (
            team.get('team_id'),
            team.get('team_name'),
            team.get('owner'),
            team.get('admin'),
            team.get('team_logo')
        ))
    
    db.commit()


def get_all_teams() -> List[TeamDB]:
    """Get all teams from database"""
    db = get_db()
    rows = db.execute("SELECT id, team_id, team_name, team_logo FROM teams ORDER BY team_name").fetchall()
    return [TeamDB(
        id=row[0],
        team_id=row[1],
        team_name=row[2],
        team_logo=row[3]
    ) for row in rows]


def get_team_by_id(team_id: int) -> Optional[TeamDB]:
    """Get a single team by ID"""
    db = get_db()
    row = db.execute("SELECT id, team_id, team_name, team_logo FROM teams WHERE id = ?", (team_id,)).fetchone()
    if not row:
        return None
    return TeamDB(
        id=row[0],
        team_id=row[1],
        team_name=row[2],
        team_logo=row[3]
    )


def get_team_by_team_id(team_id: int) -> Optional[TeamDB]:
    """Get a single team by iRacing team_id"""
    db = get_db()
    row = db.execute("SELECT id, team_id, team_name, owner, admin, team_logo FROM teams WHERE team_id = ?", (team_id,)).fetchone()
    if not row:
        return None
    return TeamDB(
        id=row[0],
        team_id=row[1],
        team_name=row[2],
        owner=row[3],
        admin=row[4],
        team_logo=row[5]
    )


# ===== EVENT REGISTRATION QUERIES =====

def register_for_event(registration_data: EventRegistrationCreate) -> EventRegistrationResponse:
    """Register a user for an event with a team, timeslot, and car"""
    db = get_db()
    
    # Verify all relationships exist
    event_row = db.execute("SELECT id FROM events WHERE id = ?", (registration_data.event_id,)).fetchone()
    if not event_row:
        raise ValueError(f"Event {registration_data.event_id} not found")
    
    user_row = db.execute("SELECT user_id FROM users WHERE user_id = ?", (registration_data.user_id,)).fetchone()
    if not user_row:
        raise ValueError(f"User {registration_data.user_id} not found")
    
    team_row = db.execute("SELECT id FROM teams WHERE team_id = ?", (registration_data.team_id,)).fetchone()
    if not team_row:
        raise ValueError(f"Team {registration_data.team_id} not found")
    
    timeslot_row = db.execute("SELECT slot_time FROM event_time_slots WHERE slot_time = ? AND event_id = ?", 
                              (registration_data.time_slot, registration_data.event_id)).fetchone()
    if not timeslot_row:
        raise ValueError(f"Time slot {registration_data.time_slot} not found for event {registration_data.event_id}")
    
    car_row = db.execute("SELECT id FROM cars WHERE id = ?", (registration_data.car_id,)).fetchone()
    if not car_row:
        raise ValueError(f"Car {registration_data.car_id} not found")
    
    # Verify car is available for this event
    car_event_row = db.execute("SELECT 1 FROM event_cars WHERE event_id = ? AND car_id = ?",
                               (registration_data.event_id, registration_data.car_id)).fetchone()
    if not car_event_row:
        raise ValueError(f"Car {registration_data.car_id} is not available for event {registration_data.event_id}")
    
    # Insert registration
    cursor = db.execute("""
        INSERT INTO event_registrations (event_id, user_id, team_id, time_slot, car_id)
        VALUES (?, ?, ?, ?, ?)
    """, (
        registration_data.event_id,
        registration_data.user_id,
        registration_data.team_id,
        registration_data.time_slot,
        registration_data.car_id
    ))
    
    db.commit()
    registration_id = cursor.lastrowid
    
    return get_registration_by_id(registration_id)


def get_registration_by_id(registration_id: int) -> Optional[EventRegistrationResponse]:
    """Get a single registration by ID"""
    db = get_db()
    row = db.execute("""
        SELECT id, event_id, user_id, team_id, time_slot, car_id, registered_at
        FROM event_registrations WHERE id = ?
    """, (registration_id,)).fetchone()
    
    if not row:
        return None
    
    return EventRegistrationResponse(
        id=row[0],
        event_id=row[1],
        user_id=row[2],
        team_id=row[3],
        time_slot=row[4],
        car_id=row[5],
        registered_at=datetime.fromisoformat(row[6])
    )


def get_registrations_for_user(user_id: int) -> List[EventRegistrationDetail]:
    """Get all event registrations for a specific user"""
    db = get_db()
    
    registrations = []
    rows = db.execute("""
        SELECT er.id, er.event_id, er.user_id, er.team_id, er.time_slot_id, er.car_id, er.registered_at
        FROM event_registrations er
        WHERE er.user_id = ?
        ORDER BY er.registered_at DESC
    """, (user_id,)).fetchall()
    
    for row in rows:
        event = get_event_by_id(row[1])
        team = get_team_by_id(row[3])
        
        timeslot_row = db.execute("SELECT slot_time FROM event_time_slots WHERE event_id = ? AND slot_time = ?", (row[1], row[4])).fetchone()
        time_slot = TimeSlot(slot_time=datetime.fromisoformat(timeslot_row[0])) if timeslot_row else None
        
        car = get_car_by_id(row[5])
        
        registrations.append(EventRegistrationDetail(
            id=row[0],
            event=event,
            user_id=row[2],
            team=team,
            time_slot=time_slot,
            car=car,
            registered_at=datetime.fromisoformat(row[6])
        ))
    
    return registrations


def get_registrations_for_event(event_id: int) -> List[EventRegistrationDetail]:
    """Get all registrations for a specific event"""
    db = get_db()
    
    registrations = []
    rows = db.execute("""
        SELECT er.id, er.event_id, er.user_id, er.team_id, er.time_slot_id, er.car_id, er.registered_at
        FROM event_registrations er
        WHERE er.event_id = ?
        ORDER BY er.registered_at DESC
    """, (event_id,)).fetchall()
    
    for row in rows:
        event = get_event_by_id(row[1])
        team = get_team_by_id(row[3])
        
        timeslot_row = db.execute("SELECT slot_time FROM event_time_slots WHERE id = ?", (row[4],)).fetchone()
        time_slot = TimeSlot(slot_time=datetime.fromisoformat(timeslot_row[0])) if timeslot_row else None
        
        car = get_car_by_id(row[5])
        
        registrations.append(EventRegistrationDetail(
            id=row[0],
            event=event,
            user_id=row[2],
            team=team,
            time_slot=time_slot,
            car=car,
            registered_at=datetime.fromisoformat(row[6])
        ))
    
    return registrations


def get_registrations_for_event_and_team(event_id: int, team_id: int) -> List[EventRegistrationDetail]:
    """Get all registrations for a specific event and team"""
    db = get_db()
    
    registrations = []
    rows = db.execute("""
        SELECT er.id, er.event_id, er.user_id, er.team_id, er.time_slot, er.car_id, er.registered_at
        FROM event_registrations er
        WHERE er.event_id = ? AND er.team_id = ?
        ORDER BY er.registered_at DESC
    """, (event_id, team_id)).fetchall()
    
    for row in rows:
        event = get_event_by_id(row[1])
        team = get_team_by_team_id(row[3])
        
        print(row[4])
        timeslot_row = row[4]
        time_slot = TimeSlot(slot_time=datetime.fromisoformat(timeslot_row)) if timeslot_row else None
        
        car = get_car_by_id(row[5])

        display_name = get_display_name_from_user_id(row[2])
        
        registrations.append(EventRegistrationDetail(
            id=row[0],
            event=event,
            display_name=display_name,
            team=team,
            time_slot=time_slot,
            car=car,
            registered_at=datetime.fromisoformat(row[6])
        ))
    
    return registrations

def get_event_registration_for_event_and_team(event_id: int, team_id: int) -> List[EventRegistrationCreate]:
    """Get event registration for a specific event and team"""
    db = get_db()
    
    rows = db.execute("""
        SELECT id, event_id, user_id, team_id, time_slot, car_id
        FROM event_registrations
        WHERE event_id = ? AND team_id = ?
    """, (event_id, team_id)).fetchall()
    
    registrations = []
    for row in rows:
        registrations.append(EventRegistrationCreate(
            id=row[0],
            event_id=row[1],
            user_id=row[2],
            team_id=row[3],
            time_slot=row[4],
            car_id=row[5]
        ))
    
    return registrations


def cancel_registration(registration_id: int) -> bool:
    """Cancel an event registration"""
    db = get_db()
    
    # Check if registration exists
    existing = db.execute("SELECT id FROM event_registrations WHERE id = ?", (registration_id,)).fetchone()
    if not existing:
        return False
    
    # Delete registration
    db.execute("DELETE FROM event_registrations WHERE id = ?", (registration_id,))
    db.commit()
    
    return True


def cancel_user_event_registration(user_id: int, event_id: int) -> bool:
    """Cancel a user's registration for a specific event"""
    db = get_db()
    
    # Find and delete the registration
    db.execute("DELETE FROM event_registrations WHERE user_id = ? AND event_id = ?", (user_id, event_id))
    db.commit()
    
    return True