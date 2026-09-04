import re
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class EventNormalizer:
    @staticmethod
    def normalize_plate(raw_plate: str) -> str:
        if not raw_plate:
            return ""
        # Remove spaces, hyphens, special chars, uppercase
        clean = re.sub(r"[^A-Za-z0-9]", "", raw_plate).upper()
        return clean

    @staticmethod
    def normalize_camera_metadata(raw_data: Dict[str, Any], vendor: str) -> Dict[str, Any]:
        """Translates vendor-specific camera attributes into canonical Schema format"""
        normalized = {
            "camera_code": raw_data.get("camera_code") or raw_data.get("id") or raw_data.get("device_id") or "CAM-UNKNOWN",
            "name": raw_data.get("name") or raw_data.get("label") or raw_data.get("channel_name") or "Camera",
            "vendor": vendor,
            "model": raw_data.get("model") or "Generic-IP-Cam",
            "protocol": raw_data.get("protocol", "RTSP").upper(),
            "codec": raw_data.get("codec", "H.264").upper(),
            "resolution": raw_data.get("resolution", "1920x1080"),
            "fps": float(raw_data.get("fps", 25.0)),
            "latitude": float(raw_data.get("latitude", 28.6139)),
            "longitude": float(raw_data.get("longitude", 77.2090)),
            "status": raw_data.get("status", "ONLINE").upper()
        }
        return normalized

    @staticmethod
    def normalize_anpr_event(raw_event: Dict[str, Any], camera_id: str) -> Dict[str, Any]:
        raw_plate = raw_event.get("plate") or raw_event.get("plate_number") or raw_event.get("license_plate") or ""
        norm_plate = EventNormalizer.normalize_plate(raw_plate)
        pts_ms = float(raw_event.get("pts_ms") or (datetime.now(timezone.utc).timestamp() * 1000))
        return {
            "camera_id": camera_id,
            "plate_number": raw_plate.upper(),
            "normalized_plate": norm_plate,
            "pts_ms": pts_ms,
            "confidence": float(raw_event.get("confidence", 0.95)),
            "vehicle_type": raw_event.get("vehicle_type", "Sedan"),
            "color": raw_event.get("color", "White"),
            "speed_kmh": float(raw_event.get("speed_kmh", 45.0)),
            "direction": raw_event.get("direction", "NORTHBOUND")
        }
