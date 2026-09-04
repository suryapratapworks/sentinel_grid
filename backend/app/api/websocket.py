"""WebSocket endpoint for real-time alert and ANPR event push."""
import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter(tags=['WebSocket'])

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
        logger.info(f'WS client connected. Total: {len(self.active)}')
    
    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
        logger.info(f'WS client disconnected. Total: {len(self.active)}')
    
    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

manager = ConnectionManager()

@router.websocket('/ws/alerts')
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint — push real-time alerts and ANPR events to browser."""
    await manager.connect(websocket)
    try:
        # Subscribe to Redis sentinel:alerts channel
        try:
            from backend.app.core.redis_client import get_redis
            r = await get_redis()
            pubsub = r.pubsub()
            await pubsub.subscribe('sentinel:alerts', 'sentinel:anpr')
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        await manager.broadcast(data)
                    except json.JSONDecodeError:
                        pass
                
                # Check if still connected
                if websocket not in manager.active:
                    break
        except Exception as e:
            logger.error(f'Redis pubsub error: {e}')
            # Fallback: keep connection open, client polls normally
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def broadcast_alert(alert_data: dict):
    """Called by alert creation to push to all WS clients immediately."""
    await manager.broadcast({'type': 'alert', 'data': alert_data})

async def broadcast_anpr(anpr_data: dict):
    """Called by ANPR pipeline to push detections to all WS clients."""
    await manager.broadcast({'type': 'anpr', 'data': anpr_data})