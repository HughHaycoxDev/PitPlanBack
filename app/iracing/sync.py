"""
Utilities to sync Cars and Tracks from iRacing API
"""
import asyncio
from typing import List
from app.iracing.client import iracing_get
from app.db.events_queries import upsert_cars, upsert_tracks


async def sync_cars_from_iracing(access_token: str) -> List[dict]:
    """
    Fetch all cars from iRacing API and sync to database
    Returns the list of cars that were synced
    """
    url = "https://members-ng.iracing.com/data/car/get"
    
    try:
        cars_data = await iracing_get(url, access_token)
        
        # Extract necessary fields from iRacing response
        processed_cars = []
        if isinstance(cars_data, list):
            for car in cars_data:
                processed_cars.append({
                    'car_id': car.get('car_id'),
                    'car_name': car.get('car_name'),
                    'logo': car.get('logo'),
                    'tank_size': 0 # 0 for now need to get this info in the future 
                })
        elif isinstance(cars_data, dict) and 'cars' in cars_data:
            for car in cars_data['cars']:
                processed_cars.append({
                    'car_id': car.get('car_id'),
                    'car_name': car.get('car_name'),
                    'logo': car.get('logo'),
                    'tank_size': car.get('max_fuel_fill_liters', 0)
                })
        
        # Upsert to database
        if processed_cars:
            upsert_cars(processed_cars)
        
        return processed_cars
    
    except Exception as e:
        print(f"Error syncing cars from iRacing API: {str(e)}")
        raise


async def sync_tracks_from_iracing(access_token: str) -> List[dict]:
    """
    Fetch all tracks from iRacing API and sync to database
    Returns the list of tracks that were synced
    """
    url = "https://members-ng.iracing.com/data/track/get"
    
    try:
        tracks_data = await iracing_get(url, access_token)
        
        # Extract necessary fields from iRacing response
        processed_tracks = []
        if isinstance(tracks_data, list):
            for track in tracks_data:
                processed_tracks.append({
                    'track_id': track.get('track_id'),
                    'track_name': track.get('track_name'),
                    'category': track.get('category'),
                    'config_name': track.get('config_name'),
                    'logo': track.get('logo'),
                    'pit_road_speed_limit': track.get('pit_road_speed_limit', 0),
                    'small_image': track.get('small_image')
                })
        elif isinstance(tracks_data, dict) and 'tracks' in tracks_data:
            for track in tracks_data['tracks']:
                processed_tracks.append({
                    'track_id': track.get('track_id'),
                    'track_name': track.get('track_name'),
                    'category': track.get('category'),
                    'config_name': track.get('config_name'),
                    'logo': track.get('logo'),
                    'pit_road_speed_limit': track.get('pit_road_speed_limit', 0),
                    'small_image': track.get('small_image')
                })
        
        # Upsert to database
        if processed_tracks:
            upsert_tracks(processed_tracks)
        
        return processed_tracks
    
    except Exception as e:
        print(f"Error syncing tracks from iRacing API: {str(e)}")
        raise


async def sync_all_iracing_data(access_token: str):
    """
    Sync both cars and tracks from iRacing API in parallel
    """
    try:
        cars, tracks = await asyncio.gather(
            sync_cars_from_iracing(access_token),
            sync_tracks_from_iracing(access_token)
        )
        return {
            'cars': cars,
            'tracks': tracks,
            'status': 'success'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
