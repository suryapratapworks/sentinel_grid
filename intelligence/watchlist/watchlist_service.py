import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.models import Watchlist, WatchlistEntry, Alert
from backend.app.schemas.schemas import AlertResponse
from analytics.anpr.plate_engine import PlateEngine

class WatchlistService:
    @staticmethod
    def check_watchlist_hit(db: Session, raw_plate: str, camera_id: str, camera_name: str, latitude: float, longitude: float, snapshot_url: Optional[str] = None, event_id: Optional[str] = None) -> Optional[Alert]:
        norm = PlateEngine.clean_plate(raw_plate)
        if not norm:
            return None

        # Query active watchlist entries matching normalized plate
        entry = db.query(WatchlistEntry).filter(
            WatchlistEntry.normalized_plate == norm,
            WatchlistEntry.active == True
        ).first()

        if not entry:
            return None

        watchlist = db.query(Watchlist).filter(Watchlist.id == entry.watchlist_id).first()
        wl_name = watchlist.name if watchlist else "Security Watchlist"

        # Create high-priority Alert
        alert = Alert(
            id=str(uuid.uuid4()),
            event_id=event_id,
            camera_id=camera_id,
            camera_name=camera_name,
            plate_number=entry.plate_number,
            alert_type="WATCHLIST_MATCH",
            priority=entry.priority or "HIGH",
            status="ACTIVE",
            watchlist_name=wl_name,
            reason=entry.reason or "Vehicle flag detected on active hotlist",
            snapshot_url=snapshot_url,
            latitude=latitude,
            longitude=longitude,
            created_at=datetime.now(timezone.utc)
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
