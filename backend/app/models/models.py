import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Role(Base):
    __tablename__ = "roles"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, index=True, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    contact_information = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cameras = relationship("Camera", back_populates="department")
    users = relationship("User", back_populates="department")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role_name = Column(String, default="SUPER_ADMIN")
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    department = relationship("Department", back_populates="users")

class Adapter(Base):
    __tablename__ = "adapters"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, index=True, nullable=False)
    adapter_type = Column(String, nullable=False) # RTSP, ONVIF, PROPRIETARY_VMS
    vendor = Column(String, nullable=False)
    version = Column(String, default="1.0.0")
    status = Column(String, default="ONLINE") # ONLINE, DEGRADED, OFFLINE
    configuration = Column(JSON, default=dict)
    event_throughput_fps = Column(Float, default=0.0)
    connected_systems_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cameras = relationship("Camera", back_populates="adapter")

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(String, primary_key=True, default=gen_uuid)
    camera_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    vendor = Column(String, default="Generic")
    model = Column(String, default="IP-CAM-1080P")
    protocol = Column(String, default="RTSP") # RTSP, ONVIF, HLS, WebRTC, VMS_FEDERATED
    codec = Column(String, default="H.264") # H.264, H.265
    resolution = Column(String, default="1920x1080")
    fps = Column(Float, default=25.0)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String, default="ONLINE") # ONLINE, OFFLINE, RECONNECTING, DEGRADED
    integration_type = Column(String, default="DIRECT_RTSP") # DIRECT_RTSP, ONVIF, VMS_ADAPTER
    adapter_id = Column(String, ForeignKey("adapters.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    department = relationship("Department", back_populates="cameras")
    adapter = relationship("Adapter", back_populates="cameras")
    streams = relationship("CameraStream", back_populates="camera", cascade="all, delete-orphan")
    sightings = relationship("VehicleSighting", back_populates="camera")

class CameraStream(Base):
    __tablename__ = "camera_streams"
    id = Column(String, primary_key=True, default=gen_uuid)
    camera_id = Column(String, ForeignKey("cameras.id"), nullable=False)
    stream_type = Column(String, default="MAIN") # MAIN, SUB, HLS, WEBRTC
    stream_url_encrypted = Column(String, nullable=False)
    codec = Column(String, default="H.264")
    resolution = Column(String, default="1920x1080")
    bitrate = Column(Integer, default=4096)
    is_active = Column(Boolean, default=True)
    reconnect_attempts = Column(Integer, default=0)
    last_pts_ms = Column(Float, default=0.0)
    last_connected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    camera = relationship("Camera", back_populates="streams")

class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, default=gen_uuid)
    event_type = Column(String, index=True, nullable=False) # ANPR_DETECTION, VEHICLE_TRACK, WATCHLIST_HIT, CAMERA_OFFLINE
    camera_id = Column(String, ForeignKey("cameras.id"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    pts_ms = Column(Float, nullable=False) # Presentation Timestamp (ADR-006)
    confidence = Column(Float, default=0.95)
    meta_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(String, primary_key=True, default=gen_uuid)
    plate_number = Column(String, unique=True, index=True, nullable=False)
    normalized_plate = Column(String, unique=True, index=True, nullable=False)
    vehicle_type = Column(String, default="Sedan") # SUV, Sedan, Truck, Motorcycle, Bus
    make_model = Column(String, default="Unknown")
    color = Column(String, default="White")
    first_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sightings = relationship("VehicleSighting", back_populates="vehicle")

class VehicleSighting(Base):
    __tablename__ = "vehicle_sightings"
    id = Column(String, primary_key=True, default=gen_uuid)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)
    camera_id = Column(String, ForeignKey("cameras.id"), nullable=False)
    event_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    pts_ms = Column(Float, nullable=False) # PTS accurate timing (Rule 4)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    confidence = Column(Float, default=0.95)
    snapshot_url = Column(String, nullable=True)
    speed_kmh = Column(Float, default=45.0)
    direction = Column(String, default="NORTHBOUND")

    vehicle = relationship("Vehicle", back_populates="sightings")
    camera = relationship("Camera", back_populates="sightings")

class Watchlist(Base):
    __tablename__ = "watchlists"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    priority = Column(String, default="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    entries = relationship("WatchlistEntry", back_populates="watchlist", cascade="all, delete-orphan")

class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"
    id = Column(String, primary_key=True, default=gen_uuid)
    watchlist_id = Column(String, ForeignKey("watchlists.id"), nullable=False)
    plate_number = Column(String, index=True, nullable=False)
    normalized_plate = Column(String, index=True, nullable=False)
    reason = Column(String, nullable=False)
    priority = Column(String, default="HIGH")
    active = Column(Boolean, default=True)
    case_reference = Column(String, default="CASE-2026-X")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    watchlist = relationship("Watchlist", back_populates="entries")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True, default=gen_uuid)
    event_id = Column(String, nullable=True)
    camera_id = Column(String, nullable=False)
    camera_name = Column(String, default="Camera")
    plate_number = Column(String, index=True, nullable=False)
    alert_type = Column(String, default="WATCHLIST_MATCH")
    priority = Column(String, default="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String, default="ACTIVE") # ACTIVE, ACKNOWLEDGED, RESOLVED, DISMISSED
    watchlist_name = Column(String, default="State Security Hotlist")
    reason = Column(String, default="Vehicle wanted in active investigation")
    snapshot_url = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(String, primary_key=True, default=gen_uuid)
    event_id = Column(String, nullable=True)
    camera_id = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    evidence_type = Column(String, default="SNAPSHOT") # SNAPSHOT, CLIP, AUDIT_LOG
    hash = Column(String, nullable=False) # SHA-256 cryptographic proof
    file_size_bytes = Column(Integer, default=0)
    meta_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
