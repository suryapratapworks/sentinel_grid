"""Stream management API — HLS and WebRTC endpoints via MediaMTX."""
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from backend.app.core.database import get_db
from backend.app.models.models import Camera
import os

router = APIRouter(prefix='/streams', tags=['Video Streams'])

MEDIAMTX_HLS_BASE = os.getenv('MEDIAMTX_HLS_BASE', 'http://localhost:8888')
MEDIAMTX_WEBRTC_BASE = os.getenv('MEDIAMTX_WEBRTC_BASE', 'http://localhost:8889')

@router.get('/{camera_id}/hls')
def get_hls_url(camera_id: str, db: Session = Depends(get_db)):
    """Get the HLS stream URL for a camera (served by MediaMTX)."""
    cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail='Camera not found')
    slug = cam.camera_code.lower().replace('-', '_')
    return {
        'camera_id': camera_id,
        'camera_code': cam.camera_code,
        'hls_url': f'{MEDIAMTX_HLS_BASE}/{slug}/index.m3u8',
        'webrtc_url': f'{MEDIAMTX_WEBRTC_BASE}/{slug}',
        'status': cam.status
    }

@router.get('/mediamtx/status')
def mediamtx_status():
    """Check if MediaMTX relay server is running."""
    import urllib.request
    try:
        resp = urllib.request.urlopen(f'http://localhost:9997/v3/paths/list', timeout=2)
        import json
        data = json.loads(resp.read())
        return {'status': 'running', 'paths': len(data.get('items', []))}
    except Exception as e:
        return {'status': 'offline', 'error': str(e),
                'note': 'Start MediaMTX: bins/mediamtx/mediamtx.exe'}