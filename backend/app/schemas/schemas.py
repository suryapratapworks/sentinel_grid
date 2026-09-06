from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str
    department_id: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class DepartmentBase(BaseModel):
    name: str
    code: str
    contact_information: Optional[str] = None

class DepartmentResponse(DepartmentBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CameraStreamCreate(BaseModel):
    stream_type: str = "MAIN"
    stream_url: str
    codec: str = "H.264"
    resolution: str = "1920x1080"
    bitrate: int = 4096

class CameraStreamResponse(BaseModel):
    id: str
    stream_type: str
    stream_url: Optional[str] = None
    codec: str
    resolution: str
    bitrate: int
    is_active: bool
    reconnect_attempts: int
    last_pts_ms: float
    last_connected_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CameraCreate(BaseModel):
    camera_code: str
    name: str
    department_id: str
    vendor: str = "Generic"
    model: str = "IP-CAM-1080P"
    protocol: str = "RTSP"
    codec: str = "H.264"
    resolution: str = "1920x1080"
    fps: float = 25.0
    latitude: float
    longitude: float
    integration_type: str = "DIRECT_RTSP"
    adapter_id: Optional[str] = None
    stream_url: Optional[str] = None

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fps: Optional[float] = None
    resolution: Optional[str] = None
    codec: Optional[str] = None

class CameraResponse(BaseModel):
    id: str
    camera_code: str
    name: str
    department_id: str
    department_name: Optional[str] = None
    vendor: str
    model: str
    protocol: str
    codec: str
    resolution: str
    fps: float
    latitude: float
    longitude: float
    status: str
    integration_type: str
    adapter_id: Optional[str] = None
    streams: List[CameraStreamResponse] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AdapterCreate(BaseModel):
    name: str
    adapter_type: str
    vendor: str
    version: str = "1.0.0"
    configuration: Dict[str, Any] = {}

class AdapterResponse(BaseModel):
    id: str
    name: str
    adapter_type: str
    vendor: str
    version: str
    status: str
    configuration: Dict[str, Any] = {}
    event_throughput_fps: float
    connected_systems_count: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DynamicCatalogueCameraItem(BaseModel):
    catalogue_id: str
    name: str
    department_code: str
    vendor: str
    codec: str # H.264, H.265
    resolution: str
    latitude: float
    longitude: float
    live_status: str # ONLINE, OFFLINE
    rtsp_url: str
    hls_url: Optional[str] = None
    webrtc_url: Optional[str] = None

class DynamicCatalogueIngestResponse(BaseModel):
    total_discovered: int
    newly_registered: int
    updated: int
    items: List[CameraResponse]

class ANPREventCreate(BaseModel):
    camera_id: str
    plate_number: str
    confidence: float = 0.95
    vehicle_type: str = "Sedan"
    color: str = "White"
    make_model: str = "Toyota Innova"
    speed_kmh: float = 45.0
    pts_ms: float
    snapshot_base64: Optional[str] = None

class VehicleSightingResponse(BaseModel):
    id: str
    camera_id: str
    camera_code: str
    camera_name: str
    timestamp: datetime
    pts_ms: float
    latitude: float
    longitude: float
    confidence: float
    snapshot_url: Optional[str] = None
    speed_kmh: float
    direction: str
    model_config = ConfigDict(from_attributes=True)

class VehicleResponse(BaseModel):
    id: str
    plate_number: str
    normalized_plate: str
    vehicle_type: str
    make_model: str
    color: str
    first_seen_at: datetime
    last_seen_at: datetime
    total_sightings: int = 0
    sightings: List[VehicleSightingResponse] = []
    model_config = ConfigDict(from_attributes=True)

class RouteNode(BaseModel):
    sequence: int
    camera_id: str
    camera_name: str
    camera_code: str
    latitude: float
    longitude: float
    timestamp: datetime
    pts_ms: float
    confidence: float
    snapshot_url: Optional[str] = None
    speed_kmh: float

class VehicleRouteResponse(BaseModel):
    plate_number: str
    normalized_plate: str
    vehicle_type: str
    make_model: str
    color: str
    total_points: int
    total_distance_km: float
    route: List[RouteNode]

class WatchlistEntryCreate(BaseModel):
    plate_number: str
    reason: str
    priority: str = "HIGH"
    case_reference: str = "CASE-2026-X"

class WatchlistEntryResponse(BaseModel):
    id: str
    watchlist_id: str
    plate_number: str
    normalized_plate: str
    reason: str
    priority: str
    active: bool
    case_reference: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WatchlistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    priority: str = "HIGH"

class WatchlistResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    priority: str
    entries_count: int = 0
    entries: List[WatchlistEntryResponse] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AlertResponse(BaseModel):
    id: str
    event_id: Optional[str] = None
    camera_id: str
    camera_name: str
    plate_number: str
    alert_type: str
    priority: str
    status: str
    watchlist_name: str
    reason: str
    snapshot_url: Optional[str] = None
    latitude: float
    longitude: float
    created_at: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class EvidenceResponse(BaseModel):
    id: str
    event_id: Optional[str] = None
    camera_id: str
    storage_path: str
    evidence_type: str
    hash: str
    file_size_bytes: int
    meta_info: Dict[str, Any] = {}
    created_at: datetime
    verification_status: str = "VERIFIED_INTEGRAL"
    model_config = ConfigDict(from_attributes=True)

class DashboardStatsResponse(BaseModel):
    total_cameras: int
    online_cameras: int
    offline_cameras: int
    active_alerts: int
    total_vehicles_detected: int
    watchlist_hits: int
    total_adapters: int
    departments_count: int
    system_health_score: float
