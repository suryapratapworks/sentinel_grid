export interface CameraStream {
  id: string;
  stream_type: string;
  codec: string;
  resolution: string;
  bitrate: number;
  is_active: boolean;
  reconnect_attempts: number;
  last_pts_ms: number;
  last_connected_at: string;
}

export interface Camera {
  id: string;
  camera_code: string;
  name: string;
  department_id: string;
  department_name?: string;
  vendor: string;
  model: string;
  protocol: string;
  codec: string;
  resolution: string;
  fps: number;
  latitude: number;
  longitude: number;
  status: 'ONLINE' | 'OFFLINE' | 'RECONNECTING' | 'DEGRADED';
  integration_type: 'DIRECT_RTSP' | 'ONVIF' | 'VMS_ADAPTER';
  adapter_id?: string;
  streams: CameraStream[];
  created_at: string;
}

export interface Adapter {
  id: string;
  name: string;
  adapter_type: string;
  vendor: string;
  version: string;
  status: string;
  configuration: Record<string, any>;
  event_throughput_fps: number;
  connected_systems_count: number;
  created_at: string;
}

export interface VehicleSighting {
  id: string;
  camera_id: string;
  camera_code: string;
  camera_name: string;
  timestamp: string;
  pts_ms: number;
  latitude: number;
  longitude: number;
  confidence: number;
  snapshot_url?: string;
  speed_kmh: number;
  direction: string;
}

export interface Vehicle {
  id: string;
  plate_number: string;
  normalized_plate: string;
  vehicle_type: string;
  make_model: string;
  color: string;
  first_seen_at: string;
  last_seen_at: string;
  total_sightings: number;
  sightings: VehicleSighting[];
}

export interface RouteNode {
  sequence: number;
  camera_id: string;
  camera_name: string;
  camera_code: string;
  latitude: number;
  longitude: number;
  timestamp: string;
  pts_ms: number;
  confidence: number;
  snapshot_url?: string;
  speed_kmh: number;
}

export interface VehicleRoute {
  plate_number: string;
  normalized_plate: string;
  vehicle_type: string;
  make_model: string;
  color: string;
  total_points: number;
  total_distance_km: number;
  route: RouteNode[];
}

export interface WatchlistEntry {
  id: string;
  watchlist_id: string;
  plate_number: string;
  normalized_plate: string;
  reason: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  active: boolean;
  case_reference: string;
  created_at: string;
}

export interface Watchlist {
  id: string;
  name: string;
  description?: string;
  priority: string;
  entries_count: number;
  entries: WatchlistEntry[];
  created_at: string;
}

export interface Alert {
  id: string;
  event_id?: string;
  camera_id: string;
  camera_name: string;
  plate_number: string;
  alert_type: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
  watchlist_name: string;
  reason: string;
  snapshot_url?: string;
  latitude: number;
  longitude: number;
  created_at: string;
  acknowledged_by?: string;
  acknowledged_at?: string;
}

export interface EvidenceItem {
  id: string;
  event_id?: string;
  camera_id: string;
  storage_path: string;
  evidence_type: 'SNAPSHOT' | 'CLIP' | 'AUDIT_LOG';
  hash: string;
  file_size_bytes: number;
  meta_info: Record<string, any>;
  created_at: string;
  verification_status: 'VERIFIED_INTEGRAL' | 'HASH_MISMATCH_TAMPERED';
}

export interface DashboardStats {
  total_cameras: number;
  online_cameras: number;
  offline_cameras: number;
  active_alerts: number;
  total_vehicles_detected: number;
  watchlist_hits: number;
  total_adapters: number;
  departments_count: number;
  system_health_score: number;
}

export interface AuthUser {
  user_id: string;
  username: string;
  role: 'SUPER_ADMIN' | 'POLICE_OPERATOR' | 'TRAFFIC_OPERATOR' | 'MUNICIPAL_VIEWER' | string;
  department_id?: string;
  department_name?: string;
  access_token: string;
}

