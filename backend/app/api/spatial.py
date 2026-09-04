"""
Spatial & Geofencing API Router — Powered by PostgreSQL & PostGIS 3.5
Provides radius search, corridor bounding box, and geofenced camera queries.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.core.database import get_db
from typing import List, Optional

router = APIRouter(prefix="/spatial", tags=["Spatial & PostGIS Geofencing"])

@router.get("/cameras/nearby")
def get_cameras_nearby(
    lat: float = Query(..., description="Latitude of center point"),
    lon: float = Query(..., description="Longitude of center point"),
    radius_km: float = Query(5.0, description="Radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Find all cameras within a given radius (km) from a central point using PostGIS.
    """
    sql = text("""
        SELECT 
            id, camera_code, name, vendor, model, protocol, codec, 
            resolution, fps, latitude, longitude, status,
            calculate_distance_km(:lat, :lon, latitude, longitude) AS distance_km
        FROM cameras
        WHERE calculate_distance_km(:lat, :lon, latitude, longitude) <= :radius_km
        ORDER BY distance_km ASC;
    """)
    
    try:
        results = db.execute(sql, {"lat": lat, "lon": lon, "radius_km": radius_km}).mappings().all()
        return {
            "center": {"latitude": lat, "longitude": lon},
            "radius_km": radius_km,
            "total_found": len(results),
            "cameras": [dict(r) for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spatial query error: {str(e)}")

@router.get("/geofence/cameras")
def get_cameras_in_polygon(
    min_lat: float = Query(..., description="Bounding box min latitude"),
    max_lat: float = Query(..., description="Bounding box max latitude"),
    min_lon: float = Query(..., description="Bounding box min longitude"),
    max_lon: float = Query(..., description="Bounding box max longitude"),
    db: Session = Depends(get_db)
):
    """
    Retrieve cameras within a rectangular bounding box / geofence.
    """
    sql = text("""
        SELECT 
            id, camera_code, name, vendor, protocol, latitude, longitude, status
        FROM cameras
        WHERE latitude BETWEEN :min_lat AND :max_lat
          AND longitude BETWEEN :min_lon AND :max_lon
        ORDER BY camera_code ASC;
    """)
    try:
        results = db.execute(sql, {
            "min_lat": min_lat, "max_lat": max_lat,
            "min_lon": min_lon, "max_lon": max_lon
        }).mappings().all()
        return {
            "bounding_box": {"min_lat": min_lat, "max_lat": max_lat, "min_lon": min_lon, "max_lon": max_lon},
            "total_cameras": len(results),
            "cameras": [dict(r) for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geofence query error: {str(e)}")

@router.get("/postgis/status")
def get_postgis_status(db: Session = Depends(get_db)):
    """Check PostGIS installation and version."""
    try:
        version_result = db.execute(text("SELECT PostGIS_Version();")).fetchone()
        version = version_result[0] if version_result else "Unknown"
        return {
            "postgis_enabled": True,
            "version": version,
            "spatial_functions": ["ST_DWithin", "ST_Distance", "calculate_distance_km", "ST_MakePoint"]
        }
    except Exception as e:
        return {
            "postgis_enabled": False,
            "error": str(e)
        }