import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Alert
from backend.app.schemas.schemas import AlertResponse
from backend.app.core.security import get_current_user_token

router = APIRouter(prefix="/alerts", tags=["Alert Center"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Alert).order_by(Alert.created_at.desc())
    if status and status != "ALL":
        query = query.filter(Alert.status == status)
    if priority and priority != "ALL":
        query = query.filter(Alert.priority == priority)
    return query.all()

@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user_token)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_by = user.get("username", "Officer-on-Duty")
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert
