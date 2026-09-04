import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Watchlist, WatchlistEntry
from backend.app.schemas.schemas import (
    WatchlistResponse, WatchlistCreate, WatchlistEntryResponse, WatchlistEntryCreate
)
from analytics.anpr.plate_engine import PlateEngine

router = APIRouter(prefix="/watchlists", tags=["Watchlist Management"])

@router.get("", response_model=List[WatchlistResponse])
def get_watchlists(db: Session = Depends(get_db)):
    watchlists = db.query(Watchlist).all()
    results = []
    for wl in watchlists:
        entries = db.query(WatchlistEntry).filter(WatchlistEntry.watchlist_id == wl.id).all()
        entry_dtos = [
            WatchlistEntryResponse(
                id=e.id,
                watchlist_id=e.watchlist_id,
                plate_number=e.plate_number,
                normalized_plate=e.normalized_plate,
                reason=e.reason,
                priority=e.priority,
                active=e.active,
                case_reference=e.case_reference,
                created_at=e.created_at
            ) for e in entries
        ]
        results.append(WatchlistResponse(
            id=wl.id,
            name=wl.name,
            description=wl.description,
            priority=wl.priority,
            entries_count=len(entry_dtos),
            entries=entry_dtos,
            created_at=wl.created_at
        ))
    return results

@router.post("", response_model=WatchlistResponse)
def create_watchlist(payload: WatchlistCreate, db: Session = Depends(get_db)):
    wl = Watchlist(
        id=str(uuid.uuid4()),
        name=payload.name,
        description=payload.description,
        priority=payload.priority
    )
    db.add(wl)
    db.commit()
    db.refresh(wl)
    return WatchlistResponse(
        id=wl.id,
        name=wl.name,
        description=wl.description,
        priority=wl.priority,
        entries_count=0,
        entries=[],
        created_at=wl.created_at
    )

@router.post("/{watchlist_id}/entries", response_model=WatchlistEntryResponse)
def add_watchlist_entry(watchlist_id: str, payload: WatchlistEntryCreate, db: Session = Depends(get_db)):
    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    fmt, norm, _ = PlateEngine.validate_and_score(payload.plate_number)
    entry = WatchlistEntry(
        id=str(uuid.uuid4()),
        watchlist_id=watchlist_id,
        plate_number=fmt,
        normalized_plate=norm,
        reason=payload.reason,
        priority=payload.priority or wl.priority,
        active=True,
        case_reference=payload.case_reference
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
