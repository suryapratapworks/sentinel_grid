import os
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.models.models import Evidence

class EvidenceLocker:
    """
    Model 4: Selective Central VMS Evidence Storage.
    Stores only critical alert snapshots/clips and generates SHA-256 cryptographic hashes for chain of custody integrity.
    """
    @staticmethod
    def calculate_sha256(data_bytes: bytes) -> str:
        return hashlib.sha256(data_bytes).hexdigest()

    @staticmethod
    def store_evidence(db: Session, camera_id: str, data_bytes: bytes, evidence_type: str = "SNAPSHOT", event_id: Optional[str] = None, meta_info: Optional[Dict[str, Any]] = None) -> Evidence:
        evidence_id = str(uuid.uuid4())
        ext = "jpg" if evidence_type == "SNAPSHOT" else "mp4"
        sub_dir = "snapshots" if evidence_type == "SNAPSHOT" else "clips"
        file_name = f"evidence_{evidence_id}.{ext}"
        storage_path = os.path.join(settings.EVIDENCE_DIR, sub_dir, file_name)

        with open(storage_path, "wb") as f:
            f.write(data_bytes)

        file_hash = EvidenceLocker.calculate_sha256(data_bytes)
        file_size = len(data_bytes)

        record = Evidence(
            id=evidence_id,
            event_id=event_id,
            camera_id=camera_id,
            storage_path=storage_path,
            evidence_type=evidence_type,
            hash=file_hash,
            file_size_bytes=file_size,
            meta_info=meta_info or {},
            created_at=datetime.now(timezone.utc)
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def verify_integrity(storage_path: str, expected_hash: str) -> bool:
        if not os.path.exists(storage_path):
            return False
        with open(storage_path, "rb") as f:
            content = f.read()
        current_hash = EvidenceLocker.calculate_sha256(content)
        return current_hash == expected_hash
