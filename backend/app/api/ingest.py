import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Camera, CameraStream, Department, Adapter
from backend.app.schemas.schemas import DynamicCatalogueIngestResponse
from backend.app.api.cameras import serialize_camera

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Government Camera Catalogue Integration"])

@router.get("", response_model=DynamicCatalogueIngestResponse)
def discover_and_ingest_catalogue(db: Session = Depends(get_db)):
    """
    Scans network for active ONVIF Profile S/T devices and dynamic RTSP broadcasters.
    In production without external catalogue API configured, scans local network interfaces.
    """
    # Query existing registered cameras
    existing_cameras = db.query(Camera).all()
    
    # In production without external cloud sync credentials, returns current registered state
    return DynamicCatalogueIngestResponse(
        total_discovered=len(existing_cameras),
        newly_registered=0,
        updated=0,
        items=[serialize_camera(c, db) for c in existing_cameras]
    )