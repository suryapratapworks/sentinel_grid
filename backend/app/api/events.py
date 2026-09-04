import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Event, Camera, Vehicle, VehicleSighting
from backend.app.schemas.schemas import ANPREventCreate
from analytics.anpr.plate_engine import PlateEngine
from intelligence.watchlist.watchlist_service import WatchlistService
from evidence.locker import EvidenceLocker

router = APIRouter(prefix="/events", tags=["Event Pipeline"])

@router.post("/simulate_anpr")
def simulate_live_anpr(payload: ANPREventCreate, db: Session = Depends(get_db)):
    cam = db.query(Camera).filter(Camera.id == payload.camera_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    fmt, norm, conf = PlateEngine.validate_and_score(payload.plate_number, payload.confidence)
    
    vehicle = db.query(Vehicle).filter(Vehicle.normalized_plate == norm).first()
    if not vehicle:
        vehicle = Vehicle(
            id=str(uuid.uuid4()),
            plate_number=fmt,
            normalized_plate=norm,
            vehicle_type=payload.vehicle_type,
            make_model=payload.make_model,
            color=payload.color,
            first_seen_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc)
        )
        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)
    else:
        vehicle.last_seen_at = datetime.now(timezone.utc)
        db.commit()

    sighting_url = "/evidence/snapshots/sighting_" + cam.camera_code.lower() + "_" + norm + ".jpg"
    sighting = VehicleSighting(
        id=str(uuid.uuid4()),
        vehicle_id=vehicle.id,
        camera_id=cam.id,
        timestamp=datetime.now(timezone.utc),
        pts_ms=payload.pts_ms,
        latitude=cam.latitude,
        longitude=cam.longitude,
        confidence=conf,
        snapshot_url=sighting_url,
        speed_kmh=payload.speed_kmh
    )
    db.add(sighting)

    event = Event(
        id=str(uuid.uuid4()),
        event_type="ANPR_DETECTION",
        camera_id=cam.id,
        timestamp=datetime.now(timezone.utc),
        pts_ms=payload.pts_ms,
        confidence=conf,
        meta_info={"plate": fmt, "normalized": norm, "vehicle_type": payload.vehicle_type}
    )
    db.add(event)
    db.commit()

    alert = WatchlistService.check_watchlist_hit(
        db=db,
        raw_plate=fmt,
        camera_id=cam.id,
        camera_name=cam.name,
        latitude=cam.latitude,
        longitude=cam.longitude,
        snapshot_url=sighting.snapshot_url,
        event_id=event.id
    )

    evidence_id = None
    if alert:
        evidence_payload = ("EVIDENCE_ALERT_" + str(alert.id) + "_" + fmt + "_" + cam.camera_code + "_" + datetime.now().isoformat()).encode()
        ev = EvidenceLocker.store_evidence(
            db=db,
            camera_id=cam.id,
            data_bytes=evidence_payload,
            evidence_type="SNAPSHOT",
            event_id=event.id,
            meta_info={"plate": fmt, "alert_id": alert.id, "watchlist": alert.watchlist_name}
        )
        evidence_id = ev.id

    return {
        "status": "PROCESSED",
        "plate_number": fmt,
        "normalized_plate": norm,
        "confidence": conf,
        "camera": cam.camera_code,
        "watchlist_match": bool(alert),
        "alert_id": alert.id if alert else None,
        "evidence_id": evidence_id
    }
