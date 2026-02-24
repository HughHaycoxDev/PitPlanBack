"""
WebSocket router for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket_manager import manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/race-plan/{race_plan_id}")
async def websocket_endpoint(websocket: WebSocket, race_plan_id: int):
    """
    WebSocket endpoint for real-time race plan updates.
    Clients connect with a race_plan_id to receive updates for that specific race.
    """
    await manager.connect(websocket, race_plan_id)
    
    try:
        # Keep the connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            # Parse incoming message (could be used for heartbeats or other client messages)
            try:
                message = json.loads(data)
                logger.debug(f"Received message from client: {message}")
            except json.JSONDecodeError:
                logger.warning(f"Received non-JSON message: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, race_plan_id)
        logger.info(f"Client disconnected from race_plan_id={race_plan_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, race_plan_id)


# Import json for JSON parsing
import json
