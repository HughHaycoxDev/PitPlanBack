from typing import Dict, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    Clients join "rooms" based on race_plan_id to receive updates for specific races.
    """
    
    def __init__(self):
        # Dictionary mapping race_plan_id to set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, race_plan_id: int):
        """Connect a client to a specific race plan room"""
        await websocket.accept()
        
        if race_plan_id not in self.active_connections:
            self.active_connections[race_plan_id] = set()
        
        self.active_connections[race_plan_id].add(websocket)
        logger.info(f"Client connected to race_plan_id={race_plan_id}. Total clients: {len(self.active_connections[race_plan_id])}")
    
    def disconnect(self, websocket: WebSocket, race_plan_id: int):
        """Disconnect a client from a specific race plan room"""
        if race_plan_id in self.active_connections:
            self.active_connections[race_plan_id].discard(websocket)
            
            # Clean up empty rooms
            if not self.active_connections[race_plan_id]:
                del self.active_connections[race_plan_id]
            
            logger.info(f"Client disconnected from race_plan_id={race_plan_id}")
    
    async def broadcast_to_room(self, race_plan_id: int, message: dict, exclude_websocket: WebSocket = None):
        """Broadcast a message to all clients in a specific race plan room"""
        if race_plan_id not in self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections[race_plan_id]:
            # Skip the sender if specified
            if exclude_websocket and connection == exclude_websocket:
                continue
            
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections[race_plan_id].discard(connection)


# Global instance
manager = ConnectionManager()
