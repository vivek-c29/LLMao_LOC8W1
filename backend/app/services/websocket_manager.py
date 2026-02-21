from fastapi import WebSocket
from typing import Dict
import json


class WebSocketManager:
    """Manages active WebSocket connections keyed by worker_id."""

    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, worker_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[worker_id] = websocket

    def disconnect(self, worker_id: int):
        self.active_connections.pop(worker_id, None)

    async def send_personal_message(self, worker_id: int, message: dict):
        websocket = self.active_connections.get(worker_id)
        if websocket:
            await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for ws in self.active_connections.values():
            await ws.send_text(json.dumps(message))


ws_manager = WebSocketManager()
