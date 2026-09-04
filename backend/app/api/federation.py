import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Adapter
from backend.app.schemas.schemas import AdapterResponse, AdapterCreate

router = APIRouter(prefix="/federation", tags=["Federation Middleware"])

@router.get("/adapters", response_model=List[AdapterResponse])
def get_adapters(db: Session = Depends(get_db)):
    return db.query(Adapter).all()

@router.post("/adapters", response_model=AdapterResponse)
def create_adapter(payload: AdapterCreate, db: Session = Depends(get_db)):
    adapter = Adapter(
        id=str(uuid.uuid4()),
        name=payload.name,
        adapter_type=payload.adapter_type,
        vendor=payload.vendor,
        version=payload.version,
        status="ONLINE",
        configuration=payload.configuration,
        event_throughput_fps=30.0,
        connected_systems_count=1
    )
    db.add(adapter)
    db.commit()
    db.refresh(adapter)
    return adapter

@router.get("/systems")
def get_connected_vms_systems(db: Session = Depends(get_db)):
    adapters = db.query(Adapter).all()
    return [
        {
            "adapter_id": a.id,
            "adapter_name": a.name,
            "adapter_type": a.adapter_type,
            "vendor": a.vendor,
            "status": a.status,
            "version": a.version,
            "connected_nodes": a.connected_systems_count,
            "event_throughput_fps": a.event_throughput_fps
        } for a in adapters
    ]
