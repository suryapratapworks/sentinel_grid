from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Camera, Alert, Vehicle, Adapter, Department
from backend.app.schemas.schemas import DashboardStatsResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard Intelligence"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_cameras = db.query(Camera).count()
    online_cameras = db.query(Camera).filter(Camera.status == "ONLINE").count()
    offline_cameras = db.query(Camera).filter(Camera.status != "ONLINE").count()
    active_alerts = db.query(Alert).filter(Alert.status == "ACTIVE").count()
    total_vehicles = db.query(Vehicle).count()
    watchlist_hits = db.query(Alert).filter(Alert.alert_type == "WATCHLIST_MATCH").count()
    total_adapters = db.query(Adapter).count()
    departments_count = db.query(Department).count()

    health_score = 100.0 if total_cameras == 0 else round((online_cameras / total_cameras) * 100.0, 1)

    return DashboardStatsResponse(
        total_cameras=total_cameras,
        online_cameras=online_cameras,
        offline_cameras=offline_cameras,
        active_alerts=active_alerts,
        total_vehicles_detected=total_vehicles,
        watchlist_hits=watchlist_hits,
        total_adapters=total_adapters,
        departments_count=departments_count,
        system_health_score=health_score
    )
