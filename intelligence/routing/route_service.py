import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.models import Vehicle, VehicleSighting, Camera
from backend.app.schemas.schemas import VehicleRouteResponse, RouteNode

class RouteReconstructionService:
    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 3)

    @staticmethod
    def reconstruct_route(db: Session, normalized_plate: str) -> Optional[Dict[str, Any]]:
        vehicle = db.query(Vehicle).filter(Vehicle.normalized_plate == normalized_plate).first()
        if not vehicle:
            return None

        # Sort strictly chronologically by PTS/timestamp (Rule 4 / PRD Section 6.3)
        sightings = (
            db.query(VehicleSighting)
            .filter(VehicleSighting.vehicle_id == vehicle.id)
            .order_by(VehicleSighting.timestamp.asc(), VehicleSighting.pts_ms.asc())
            .all()
        )

        nodes: List[Dict[str, Any]] = []
        total_distance = 0.0

        for idx, s in enumerate(sightings):
            cam = db.query(Camera).filter(Camera.id == s.camera_id).first()
            cam_name = cam.name if cam else "Camera Sighting"
            cam_code = cam.camera_code if cam else "CAM-UNK"

            node = {
                "sequence": idx + 1,
                "camera_id": s.camera_id,
                "camera_name": cam_name,
                "camera_code": cam_code,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "timestamp": s.timestamp,
                "pts_ms": s.pts_ms,
                "confidence": s.confidence,
                "snapshot_url": s.snapshot_url,
                "speed_kmh": s.speed_kmh
            }
            nodes.append(node)

            if idx > 0:
                dist = RouteReconstructionService.haversine_km(
                    nodes[idx-1]["latitude"], nodes[idx-1]["longitude"],
                    s.latitude, s.longitude
                )
                total_distance += dist

        return {
            "plate_number": vehicle.plate_number,
            "normalized_plate": vehicle.normalized_plate,
            "vehicle_type": vehicle.vehicle_type,
            "make_model": vehicle.make_model,
            "color": vehicle.color,
            "total_points": len(nodes),
            "total_distance_km": round(total_distance, 2),
            "route": nodes
        }