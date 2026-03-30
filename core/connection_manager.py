from typing import Dict, List
from fastapi import WebSocket
from utils.logger import logger_instance as logger
import json
import asyncio

class ConnectionManager:
    """
    Manages WebSocket connections and acts as a message broker
    between backend core logic and the WebSocket API.
    """
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connection_metadata: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        
        self.active_connections[client_id].append(websocket)
        self.connection_metadata[client_id] = {
            "connected_at": str(asyncio.get_event_loop().time()),
            "message_count": 0
        }
        
        logger.info(f"Client {client_id} connected. Total connections: {self.get_connection_count()}")

    def disconnect(self, websocket: WebSocket, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            if websocket in self.active_connections[client_id]:
                self.active_connections[client_id].remove(websocket)
            
            # Clean up if no more connections for this client
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
                if client_id in self.connection_metadata:
                    del self.connection_metadata[client_id]
        
        logger.info(f"Client {client_id} disconnected. Total connections: {self.get_connection_count()}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")

    async def send_to_client(self, message: Dict, client_id: str):
        """Send a message to all connections of a specific client"""
        if client_id in self.active_connections:
            message_str = json.dumps(message)
            disconnected = []
            
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_text(message_str)
                    if client_id in self.connection_metadata:
                        self.connection_metadata[client_id]["message_count"] += 1
                except Exception as e:
                    logger.error(f"Error sending to client {client_id}: {str(e)}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, client_id)

    async def broadcast(self, message: Dict):
        """Broadcast a message to all connected clients"""
        message_str = json.dumps(message)
        disconnected = []
        
        for client_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {str(e)}")
                    disconnected.append((connection, client_id))
        
        # Clean up disconnected connections
        for conn, client_id in disconnected:
            self.disconnect(conn, client_id)

    async def stream_token(self, token: str, client_id: str, message_type: str = "token"):
        """Stream a single token to a client (for real-time LLM responses)"""
        message = {
            "type": message_type,
            "content": token,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        await self.send_to_client(message, client_id)

    async def send_log(self, log_message: str, client_id: str, log_level: str = "info"):
        """Send a log message to a specific client"""
        message = {
            "type": "log",
            "level": log_level,
            "content": log_message,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        await self.send_to_client(message, client_id)

    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())

    def get_client_count(self) -> int:
        """Get number of unique clients"""
        return len(self.active_connections)

    def get_connection_info(self) -> Dict:
        """Get information about all connections"""
        return {
            "total_connections": self.get_connection_count(),
            "total_clients": self.get_client_count(),
            "clients": {
                client_id: {
                    "connection_count": len(connections),
                    "metadata": self.connection_metadata.get(client_id, {})
                }
                for client_id, connections in self.active_connections.items()
            }
        }

# Global instance
connection_manager = ConnectionManager()
