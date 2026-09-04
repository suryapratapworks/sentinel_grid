import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Vehicle, VehicleSighting, Camera
from backend.app.schemas.schemas import VehicleResponse, VehicleRouteResponse, VehicleSightingResponse
from analytics.anpr.plate_engine import PlateEngine
from intelligence.routing.route_service import RouteReconstructionService

router = APIRouter(prefix="/vehicles", tags=["Vehicle Intelligence"])

@router.get("/search", response_model=List[VehicleResponse])
def search_vehicles(
    plate: Optional[str] = Query(None, description="Vehicle registration plate query"),
    db: Session = Depends(get_db)
):
    query = db.query(Vehicle)
    if plate:
        norm = PlateEngine.clean_plate(plate)
        query = query.filter(
            (Vehicle.normalized_plate.contains(norm)) | 
            (Vehicle.plate_number.contains(plate.upper()))
        )

    vehicles = query.all()
    results = []

    for v in vehicles:
        sightings = (
            db.query(VehicleSighting)
            .filter(VehicleSighting.vehicle_id == v.id)
            .order_by(VehicleSighting.timestamp.desc())
            .all()
        )
        sighting_dtos = []
        for s in sightings:
            cam = db.query(Camera).filter(Camera.id == s.camera_id).first()
            sighting_dtos.append(VehicleSightingResponse(
                id=s.id,
                camera_id=s.camera_id,
                camera_code=cam.camera_code if cam else "CAM-UNK",
                camera_name=cam.name if cam else "Camera Sighting",
                timestamp=s.timestamp,
                pts_ms=s.pts_ms,
                latitude=s.latitude,
                longitude=s.longitude,
                confidence=s.confidence,
                snapshot_url=s.snapshot_url,
                speed_kmh=s.speed_kmh,
                direction=s.direction
            ))

        results.append(VehicleResponse(
            id=v.id,
            plate_number=v.plate_number,
            normalized_plate=v.normalized_plate,
            vehicle_type=v.vehicle_type,
            make_model=v.make_model,
            color=v.color,
            first_seen_at=v.first_seen_at,
            last_seen_at=v.last_seen_at,
            total_sightings=len(sighting_dtos),
            sightings=sighting_dtos
        ))

    return results

@router.get("/{plate}/route", response_model=VehicleRouteResponse)
def get_vehicle_route(plate: str, db: Session = Depends(get_db)):
    norm = PlateEngine.clean_plate(plate)
    route_data = RouteReconstructionService.reconstruct_route(db, norm)
    if not route_data:
        raise HTTPException(status_code=404, detail="No movement trajectory found for vehicle " + plate)
    return route_data
