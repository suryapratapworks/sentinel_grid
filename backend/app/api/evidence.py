from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Evidence
from backend.app.schemas.schemas import EvidenceResponse
from evidence.locker import EvidenceLocker

router = APIRouter(prefix="/evidence", tags=["Evidence Locker"])

@router.get("", response_model=List[EvidenceResponse])
def get_evidence_list(db: Session = Depends(get_db)):
    records = db.query(Evidence).order_by(Evidence.created_at.desc()).all()
    results = []
    for r in records:
        integral = EvidenceLocker.verify_integrity(r.storage_path, r.hash)
        status_text = "VERIFIED_INTEGRAL" if integral else "HASH_MISMATCH_TAMPERED"
        results.append(EvidenceResponse(
            id=r.id,
            event_id=r.event_id,
            camera_id=r.camera_id,
            storage_path=r.storage_path,
            evidence_type=r.evidence_type,
            hash=r.hash,
            file_size_bytes=r.file_size_bytes,
            meta_info=r.meta_info or {},
            created_at=r.created_at,
            verification_status=status_text
        ))
    return results
