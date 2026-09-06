import uuid
import urllib.request
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Camera, CameraStream, Department, Adapter, Event, VehicleSighting, Alert, Evidence
from backend.app.schemas.schemas import CameraResponse, CameraCreate, CameraUpdate, CameraStreamResponse
from backend.app.core.security import get_current_user_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cameras", tags=["Camera Registry"])

def sync_mediamtx_path(camera_code: str, stream_url: str):
    """Dynamically register or update the stream path in MediaMTX relay."""
    slug = camera_code.lower().replace("-", "_")
    try:
        # Try add path
        url = f"http://localhost:9997/v3/config/paths/add/{slug}"
        payload = json.dumps({"source": stream_url, "sourceOnDemand": True}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=2)
        logger.info(f"MediaMTX path registered: {slug} -> {stream_url}")
    except Exception:
        try:
            # If path already exists, replace it
            url = f"http://localhost:9997/v3/config/paths/replace/{slug}"
            payload = json.dumps({"source": stream_url, "sourceOnDemand": True}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=2)
            logger.info(f"MediaMTX path replaced: {slug} -> {stream_url}")
        except Exception as e:
            logger.warning(f"Could not sync MediaMTX path {slug}: {e}")

def remove_mediamtx_path(camera_code: str):
    """Remove a stream path from MediaMTX relay on camera deletion."""
    slug = camera_code.lower().replace("-", "_")
    try:
        url = f"http://localhost:9997/v3/config/paths/delete/{slug}"
        req = urllib.request.Request(url, headers={"Content-Type": "application/json"}, method="DELETE")
        urllib.request.urlopen(req, timeout=2)
        logger.info(f"MediaMTX path removed: {slug}")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            logger.warning(f"Could not delete MediaMTX path {slug}: {e}")
    except Exception as e:
        logger.warning(f"Could not delete MediaMTX path {slug}: {e}")

def serialize_camera(cam: Camera, db: Session) -> CameraResponse:
    dept = db.query(Department).filter(Department.id == cam.department_id).first()
    streams = db.query(CameraStream).filter(CameraStream.camera_id == cam.id).all()
    stream_dtos = [
        CameraStreamResponse(
            id=s.id,
            stream_type=s.stream_type,
            codec=s.codec,
            resolution=s.resolution,
            bitrate=s.bitrate,
            is_active=s.is_active,
            reconnect_attempts=s.reconnect_attempts,
            last_pts_ms=s.last_pts_ms,
            last_connected_at=s.last_connected_at
        ) for s in streams
    ]
    return CameraResponse(
        id=cam.id,
        camera_code=cam.camera_code,
        name=cam.name,
        department_id=cam.department_id,
        department_name=dept.name if dept else "General",
        vendor=cam.vendor,
        model=cam.model,
        protocol=cam.protocol,
        codec=cam.codec,
        resolution=cam.resolution,
        fps=cam.fps,
        latitude=cam.latitude,
        longitude=cam.longitude,
        status=cam.status,
        integration_type=cam.integration_type,
        adapter_id=cam.adapter_id,
        streams=stream_dtos,
        created_at=cam.created_at
    )

@router.get("", response_model=List[CameraResponse])
def get_cameras(
    department_id: Optional[str] = None,
    status: Optional[str] = None,
    protocol: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user_token)
):
    query = db.query(Camera)
    if department_id and department_id != "ALL":
        query = query.filter(Camera.department_id == department_id)
    if status and status != "ALL":
        query = query.filter(Camera.status == status)
    if protocol and protocol != "ALL":
        query = query.filter(Camera.protocol == protocol)

    cameras = query.all()
    return [serialize_camera(c, db) for c in cameras]

@router.get("/departments/list")
def get_departments_list(db: Session = Depends(get_db)):
    departments = db.query(Department).all()
    return [{"id": d.id, "name": d.name, "code": d.code} for d in departments]

@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera_by_id(camera_id: str, db: Session = Depends(get_db)):
    cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return serialize_camera(cam, db)

@router.post("", response_model=CameraResponse)
def create_camera(payload: CameraCreate, db: Session = Depends(get_db)):
    # Check duplicate code
    existing = db.query(Camera).filter(Camera.camera_code == payload.camera_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Camera code '{payload.camera_code}' already exists")

    cam_id = str(uuid.uuid4())
    cam = Camera(
        id=cam_id,
        camera_code=payload.camera_code,
        name=payload.name,
        department_id=payload.department_id,
        vendor=payload.vendor,
        model=payload.model,
        protocol=payload.protocol,
        codec=payload.codec,
        resolution=payload.resolution,
        fps=payload.fps,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status="ONLINE",
        integration_type=payload.integration_type,
        adapter_id=payload.adapter_id
    )
    db.add(cam)

    stream_url = payload.stream_url or f"rtsp://stream-gateway.state.gov:8554/live/{payload.camera_code.lower()}"
    stream = CameraStream(
        id=str(uuid.uuid4()),
        camera_id=cam_id,
        stream_type="MAIN",
        stream_url_encrypted=stream_url,
        codec=payload.codec,
        resolution=payload.resolution,
        bitrate=4096,
        is_active=True
    )
    db.add(stream)
    db.commit()
    db.refresh(cam)

    # Automatically register stream relay in MediaMTX
    sync_mediamtx_path(cam.camera_code, stream_url)

    return serialize_camera(cam, db)

@router.patch("/{camera_id}", response_model=CameraResponse)
def update_camera(camera_id: str, payload: CameraUpdate, db: Session = Depends(get_db)):
    cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cam, key, value)

    db.commit()
    db.refresh(cam)
    return serialize_camera(cam, db)

@router.delete("/purge/all")
def purge_all_cameras(
    db: Session = Depends(get_db)
):
    """Purge all cameras, streams, sightings, alerts, and events from the live registry."""
    db.query(Alert).delete(synchronize_session=False)
    db.query(Evidence).delete(synchronize_session=False)
    db.query(VehicleSighting).delete(synchronize_session=False)
    db.query(Event).delete(synchronize_session=False)
    db.query(CameraStream).delete(synchronize_session=False)
    db.query(Camera).delete(synchronize_session=False)
    db.commit()
    return {"status": "purged", "message": "All cameras and associated data successfully purged from live registry."}

@router.delete("/{camera_id}")
def delete_camera(
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_token)
):
    """Delete a camera from the registry."""
    cam = db.query(Camera).filter(Camera.id == camera_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    camera_code = cam.camera_code

    # Clean up associated alerts, evidence, sightings, events, and stream records
    db.query(Alert).filter(Alert.camera_id == camera_id).delete(synchronize_session=False)
    db.query(Evidence).filter(Evidence.camera_id == camera_id).delete(synchronize_session=False)
    db.query(VehicleSighting).filter(VehicleSighting.camera_id == camera_id).delete(synchronize_session=False)
    db.query(Event).filter(Event.camera_id == camera_id).delete(synchronize_session=False)
    db.query(CameraStream).filter(CameraStream.camera_id == camera_id).delete(synchronize_session=False)

    db.delete(cam)
    db.commit()

    # Deregister from MediaMTX relay
    remove_mediamtx_path(camera_code)

    return {
        "status": "deleted",
        "camera_id": camera_id,
        "camera_code": camera_code,
        "message": f"Camera '{camera_code}' permanently deleted."
    }
