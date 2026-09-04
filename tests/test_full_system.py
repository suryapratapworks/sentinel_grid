"""
SENTINEL GRID — Full System Automated Verification & Integration Test Suite
Tests all 4 architectural models, REST API gateways, authentication & RBAC,
geospatial PostGIS analytics, AI ANPR engine, and cryptographic evidence vault.
"""

import os
import uuid
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.services.seed_data import seed_database
from backend.app.models.models import Camera, Department, Watchlist, WatchlistEntry, Vehicle, VehicleSighting, Evidence
from analytics.anpr.plate_engine import PlateEngine
from evidence.locker import EvidenceLocker
from federation.adapters.rtsp_adapter import RTSPAdapter

@pytest.fixture(scope="session")
def client():
    """Initializes the database schema, seeds standard baseline, and yields TestClient."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()
    
    with TestClient(app) as test_client:
        yield test_client

# ==============================================================================
# Tier 1: Health & Diagnostics
# ==============================================================================
def test_system_health(client):
    """Verify health endpoint, versioning, and core subsystems."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["version"] == "2.0.0"
    assert data["components"]["api"] == "ok"
    assert data["components"]["database"] == "ok"
    assert data["components"]["redis"] == "fakeredis"

# ==============================================================================
# Tier 2: Authentication & RBAC Governance
# ==============================================================================
def test_authentication_and_rbac_flow(client):
    """Verify JWT authentication, credential validation, and role-based access tokens."""
    # Test valid Super Admin login
    admin_login = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert admin_login.status_code == 200
    admin_data = admin_login.json()
    assert "access_token" in admin_data
    assert admin_data["role"] == "SUPER_ADMIN"
    assert admin_data["username"] == "admin"

    # Test valid Investigator login
    inv_login = client.post("/api/auth/login", json={"username": "investigator", "password": "investigator123"})
    assert inv_login.status_code == 200
    assert inv_login.json()["role"] == "INVESTIGATOR"

    # Test valid Operator login
    op_login = client.post("/api/auth/login", json={"username": "operator", "password": "operator123"})
    assert op_login.status_code == 200
    assert op_login.json()["role"] == "TRAFFIC_OPERATOR"

    # Test valid Municipal Viewer login
    viewer_login = client.post("/api/auth/login", json={"username": "municipal_viewer", "password": "viewer123"})
    assert viewer_login.status_code == 200
    assert viewer_login.json()["role"] == "MUNICIPAL_VIEWER"

    # Test invalid password rejection
    bad_login = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert bad_login.status_code == 401
    assert "Invalid username or password" in bad_login.json()["detail"]

# ==============================================================================
# Tier 3: Model 1 — Camera Registry & Telemetry Lifecycle
# ==============================================================================
def test_camera_registry_lifecycle(client):
    """Test camera onboarding, retrieval, filtering, and telemetry updates."""
    # Get official department
    db = SessionLocal()
    dept = db.query(Department).first()
    dept_id = dept.id if dept else "dept-tpd"
    db.close()

    cam_suffix = uuid.uuid4().hex[:6].upper()
    cam_payload = {
        "camera_code": f"CAM-E2E-{cam_suffix}",
        "name": f"Connaught Place Intersection {cam_suffix}",
        "department_id": dept_id,
        "vendor": "Axis Communications",
        "model": "P1455-LE",
        "protocol": "RTSP",
        "codec": "H.264",
        "resolution": "1920x1080",
        "fps": 30.0,
        "latitude": 28.6315,
        "longitude": 77.2167,
        "integration_type": "DIRECT_RTSP",
        "stream_url": "rtsp://127.0.0.1:8554/test_stream"
    }

    # Register camera
    create_resp = client.post("/api/cameras", json=cam_payload)
    assert create_resp.status_code == 200
    cam = create_resp.json()
    cam_id = cam["id"]
    assert cam["camera_code"] == cam_payload["camera_code"]
    assert cam["fps"] == 30.0
    assert cam["status"] == "ONLINE"
    assert len(cam["streams"]) > 0

    # Retrieve camera by ID
    get_resp = client.get(f"/api/cameras/{cam_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == cam_id

    # List cameras and verify presence
    list_resp = client.get("/api/cameras")
    assert list_resp.status_code == 200
    cam_ids = [c["id"] for c in list_resp.json()]
    assert cam_id in cam_ids

    # Update camera telemetry
    update_resp = client.patch(f"/api/cameras/{cam_id}", json={
        "name": f"Connaught Place Updated {cam_suffix}",
        "fps": 25.0,
        "resolution": "1280x720"
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["fps"] == 25.0
    assert update_resp.json()["resolution"] == "1280x720"

# ==============================================================================
# Tier 4: Model 2 — AI ANPR Detection, Ingestion, & Sightings
# ==============================================================================
def test_anpr_event_simulation_and_vehicle_sighting(client):
    """Test edge AI detection ingestion, normalization, and sighting persistence."""
    # Retrieve a registered camera
    cams = client.get("/api/cameras").json()
    assert len(cams) > 0
    cam = cams[0]

    suffix = uuid.uuid4().hex[:4].upper()
    test_plate = f"DL 01 AB {suffix}"

    event_payload = {
        "camera_id": cam["id"],
        "plate_number": test_plate,
        "confidence": 0.96,
        "vehicle_type": "SUV",
        "color": "Midnight Black",
        "make_model": "Mahindra Scorpio-N",
        "speed_kmh": 58.5,
        "pts_ms": 102450.0
    }

    sim_resp = client.post("/api/events/simulate_anpr", json=event_payload)
    assert sim_resp.status_code == 200
    res = sim_resp.json()
    assert res["status"] == "PROCESSED"
    assert res["confidence"] == 0.96
    assert res["normalized_plate"] == f"DL01AB{suffix}"

    # Search vehicle by plate
    search_resp = client.get(f"/api/vehicles/search?plate=DL01AB{suffix}")
    assert search_resp.status_code == 200
    vehicles = search_resp.json()
    assert len(vehicles) >= 1
    found = vehicles[0]
    assert found["vehicle_type"] == "SUV"
    assert found["make_model"] == "Mahindra Scorpio-N"
    assert len(found["sightings"]) >= 1

# ==============================================================================
# Tier 5: Watchlist Triggering & Real-Time Alert Workflow
# ==============================================================================
def test_watchlist_management_and_realtime_alert(client):
    """Test creating a watchlist, adding wanted plate, triggering alert on ANPR event, and acknowledging alert."""
    # 1. Create a high-priority watchlist
    wl_payload = {
        "name": f"Stolen Luxury Vehicles Test {uuid.uuid4().hex[:4]}",
        "description": "Automated system test watchlist",
        "priority": "CRITICAL"
    }
    wl_resp = client.post("/api/watchlists", json=wl_payload)
    assert wl_resp.status_code == 200
    wl_id = wl_resp.json()["id"]

    # 2. Add suspect plate entry
    suspect_suffix = uuid.uuid4().hex[:4].upper()
    suspect_plate = f"MH 12 CR {suspect_suffix}"
    entry_payload = {
        "plate_number": suspect_plate,
        "reason": "Armed robbery getaway vehicle",
        "priority": "CRITICAL",
        "case_reference": f"FIR-2026-{suspect_suffix}"
    }
    entry_resp = client.post(f"/api/watchlists/{wl_id}/entries", json=entry_payload)
    assert entry_resp.status_code == 200
    assert entry_resp.json()["normalized_plate"] == f"MH12CR{suspect_suffix}"

    # 3. Simulate ANPR sighting of suspect plate
    cams = client.get("/api/cameras").json()
    cam = cams[0]
    anpr_payload = {
        "camera_id": cam["id"],
        "plate_number": suspect_plate.lower().replace(" ", "-"),  # Test with noisy raw input
        "confidence": 0.98,
        "vehicle_type": "Sedan",
        "color": "Silver",
        "make_model": "Honda City",
        "speed_kmh": 65.0,
        "pts_ms": 204500.0
    }
    detection_resp = client.post("/api/events/simulate_anpr", json=anpr_payload)
    assert detection_resp.status_code == 200
    det_data = detection_resp.json()
    assert det_data["watchlist_match"] is True
    assert det_data["alert_id"] is not None
    assert det_data["evidence_id"] is not None
    alert_id = det_data["alert_id"]

    # 4. Verify Alert in Alert Center
    alerts_resp = client.get("/api/alerts?status=ACTIVE")
    assert alerts_resp.status_code == 200
    active_alerts = alerts_resp.json()
    matched = [a for a in active_alerts if a["id"] == alert_id]
    assert len(matched) == 1
    alert = matched[0]
    assert alert["priority"] == "CRITICAL"
    assert alert["status"] == "ACTIVE"

    # 5. Acknowledge Alert by officer
    ack_resp = client.patch(f"/api/alerts/{alert_id}/acknowledge")
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "ACKNOWLEDGED"

# ==============================================================================
# Tier 6: Spatio-Temporal Route Corridor Reconstruction
# ==============================================================================
def test_vehicle_route_reconstruction_chronology(client):
    """Test chronological corridor reconstruction using Presentation Timestamps (PTS)."""
    db = SessionLocal()
    dept = db.query(Department).first()
    dept_id = dept.id if dept else "dept-tpd"
    
    # Create 3 sequential cameras along Delhi corridor
    suffix = uuid.uuid4().hex[:6].upper()
    c1 = Camera(id=str(uuid.uuid4()), camera_code=f"ROUTE-A-{suffix}", name="Toll Plaza Entry", department_id=dept_id, vendor="Axis", protocol="RTSP", codec="H.264", resolution="1080p", fps=25.0, latitude=28.5355, longitude=77.3910, status="ONLINE", integration_type="DIRECT_RTSP")
    c2 = Camera(id=str(uuid.uuid4()), camera_code=f"ROUTE-B-{suffix}", name="Expressway KM 12", department_id=dept_id, vendor="Axis", protocol="RTSP", codec="H.264", resolution="1080p", fps=25.0, latitude=28.5672, longitude=77.3521, status="ONLINE", integration_type="DIRECT_RTSP")
    c3 = Camera(id=str(uuid.uuid4()), camera_code=f"ROUTE-C-{suffix}", name="City Ring Interchange", department_id=dept_id, vendor="Axis", protocol="RTSP", codec="H.264", resolution="1080p", fps=25.0, latitude=28.6139, longitude=77.2090, status="ONLINE", integration_type="DIRECT_RTSP")
    db.add_all([c1, c2, c3])
    db.commit()

    test_plate = f"HR-26-TR-{suffix[:4]}"
    norm_plate = f"HR26TR{suffix[:4]}"
    v = Vehicle(id=str(uuid.uuid4()), plate_number=test_plate, normalized_plate=norm_plate, vehicle_type="SEDAN", make_model="Skoda Superb", color="Blue")
    db.add(v)
    db.commit()

    # Add sightings in scrambled order to test sorting
    s3 = VehicleSighting(id=str(uuid.uuid4()), vehicle_id=v.id, camera_id=c3.id, pts_ms=150000.0, latitude=c3.latitude, longitude=c3.longitude, confidence=0.99, speed_kmh=60.0)
    s1 = VehicleSighting(id=str(uuid.uuid4()), vehicle_id=v.id, camera_id=c1.id, pts_ms=50000.0, latitude=c1.latitude, longitude=c1.longitude, confidence=0.98, speed_kmh=72.0)
    s2 = VehicleSighting(id=str(uuid.uuid4()), vehicle_id=v.id, camera_id=c2.id, pts_ms=100000.0, latitude=c2.latitude, longitude=c2.longitude, confidence=0.97, speed_kmh=85.0)
    db.add_all([s3, s1, s2])
    db.commit()
    db.close()

    # Query route reconstruction endpoint
    route_resp = client.get(f"/api/vehicles/{norm_plate}/route")
    assert route_resp.status_code == 200
    route_data = route_resp.json()
    assert route_data["total_points"] == 3
    assert route_data["total_distance_km"] > 0
    pts_sequence = [node["pts_ms"] for node in route_data["route"]]
    assert pts_sequence == sorted(pts_sequence)
    assert pts_sequence[0] == 50000.0
    assert pts_sequence[1] == 100000.0
    assert pts_sequence[2] == 150000.0

# ==============================================================================
# Tier 7: Model 4 — Cryptographic Evidence Locker & Tamper Detection
# ==============================================================================
def test_cryptographic_evidence_locker_and_tamper_proofing(client):
    """Test SHA-256 evidence hashing, storage, integrity verification, and tamper detection."""
    db = SessionLocal()
    payload = b"OFFICIAL_COURT_EXHIBIT_FRAME_DATA_E2E_TEST"
    ev = EvidenceLocker.store_evidence(
        db=db,
        camera_id="cam-courtroom-01",
        data_bytes=payload,
        evidence_type="SNAPSHOT",
        meta_info={"case": "STATE_VS_SUSPECT_2026", "officer": "Insp. Sharma"}
    )
    db.close()

    # Verify SHA-256 length (64 hex characters)
    assert len(ev.hash) == 64
    assert EvidenceLocker.verify_integrity(ev.storage_path, ev.hash) is True

    # Test via REST endpoint
    ev_list_resp = client.get("/api/evidence")
    assert ev_list_resp.status_code == 200
    records = ev_list_resp.json()
    stored = [r for r in records if r["id"] == ev.id]
    assert len(stored) == 1
    assert stored[0]["verification_status"] == "VERIFIED_INTEGRAL"

    # Negative Test: Tamper with evidence file content on disk
    with open(ev.storage_path, "wb") as f:
        f.write(b"TAMPERED_MODIFIED_DATA_BYTE_ATTACK")

    # Integrity verification must now detect tampering
    assert EvidenceLocker.verify_integrity(ev.storage_path, ev.hash) is False
    tampered_list = client.get("/api/evidence").json()
    tampered_record = [r for r in tampered_list if r["id"] == ev.id][0]
    assert tampered_record["verification_status"] == "HASH_MISMATCH_TAMPERED"

# ==============================================================================
# Tier 8: Model 3 — Federated Integration Middleware
# ==============================================================================
def test_federation_middleware_and_systems(client):
    """Test multi-VMS federation adapters and dynamic catalogue discovery."""
    # List seeded federation adapters
    adapters_resp = client.get("/api/federation/adapters")
    assert adapters_resp.status_code == 200
    adapters = adapters_resp.json()
    assert len(adapters) >= 4  # RTSP, ONVIF, Milestone, Genetec
    vendors = {a["vendor"] for a in adapters}
    assert "Milestone Systems" in vendors
    assert any("Genetec" in v for v in vendors)

    # Register custom adapter
    new_adapter_payload = {
        "name": "State Border Toll VMS",
        "adapter_type": "HIGHWAY_VMS",
        "vendor": "Siemens Mobility",
        "version": "4.2.0",
        "configuration": {"port": 554, "transport": "TCP"}
    }
    post_adapter = client.post("/api/federation/adapters", json=new_adapter_payload)
    assert post_adapter.status_code == 200
    assert post_adapter.json()["vendor"] == "Siemens Mobility"

    # Query connected systems summary
    systems_resp = client.get("/api/federation/systems")
    assert systems_resp.status_code == 200
    systems = systems_resp.json()
    assert len(systems) >= 5

    # Test dynamic catalogue ingestion endpoint
    ingest_resp = client.get("/api/ingest")
    assert ingest_resp.status_code == 200
    ingest_data = ingest_resp.json()
    assert ingest_data["total_discovered"] >= 0
    assert isinstance(ingest_data["items"], list)

# ==============================================================================
# Tier 9: Dashboard Aggregation & System KPIs
# ==============================================================================
def test_dashboard_statistics(client):
    """Verify system-wide health score, camera telemetry, and active alert counters."""
    stats_resp = client.get("/api/dashboard/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total_cameras"] >= 0
    assert stats["online_cameras"] >= 0
    assert stats["active_alerts"] >= 0
    assert stats["total_vehicles_detected"] >= 0
    assert stats["departments_count"] >= 4
    assert 0.0 <= stats["system_health_score"] <= 100.0

# ==============================================================================
# Tier 10: Video Stream Relay & MediaMTX Endpoints
# ==============================================================================
def test_stream_endpoints(client):
    """Test HLS/WebRTC streaming endpoints and MediaMTX status."""
    cams = client.get("/api/cameras").json()
    assert len(cams) > 0
    cam_id = cams[0]["id"]

    stream_resp = client.get(f"/api/streams/{cam_id}/hls")
    assert stream_resp.status_code == 200
    s_data = stream_resp.json()
    assert "hls_url" in s_data
    assert "webrtc_url" in s_data
    assert s_data["hls_url"].endswith(".m3u8")

    # MediaMTX relay status check
    mmtx_resp = client.get("/api/streams/mediamtx/status")
    assert mmtx_resp.status_code == 200
    assert "status" in mmtx_resp.json()

# ==============================================================================
# Tier 11: PostGIS & Spatial Query Endpoints
# ==============================================================================
def test_spatial_query_endpoints(client):
    """Test geofence bounding boxes and PostGIS status."""
    # PostGIS status endpoint
    postgis_resp = client.get("/api/spatial/postgis/status")
    assert postgis_resp.status_code == 200
    assert "postgis_enabled" in postgis_resp.json()

    # Geofence bounding box around Delhi NCR
    geofence_resp = client.get("/api/spatial/geofence/cameras?min_lat=28.0&max_lat=29.0&min_lon=76.5&max_lon=78.0")
    assert geofence_resp.status_code == 200
    geo_data = geofence_resp.json()
    assert "total_cameras" in geo_data
    assert isinstance(geo_data["cameras"], list)

    # Spatial radius query
    radius_resp = client.get("/api/spatial/cameras/nearby?lat=28.6139&lon=77.2090&radius_km=10.0")
    assert radius_resp.status_code == 200
    assert "total_found" in radius_resp.json()

# ==============================================================================
# Tier 12: Indian License Plate Normalization Matrix
# ==============================================================================
@pytest.mark.parametrize("raw_input, expected_clean, expected_formatted", [
    ("dl 01 ab 1234", "DL01AB1234", "DL-01-AB-1234"),
    ("dl-01-ab-1234", "DL01AB1234", "DL-01-AB-1234"),
    ("hr 26 dq 5555", "HR26DQ5555", "HR-26-DQ-5555"),
    ("MH12DE1433", "MH12DE1433", "MH-12-DE-1433"),
    ("UP 16 Z 9999", "UP16Z9999", "UP-16-Z-9999"),
    ("KA-03-HA-0001", "KA03HA0001", "KA-03-HA-0001")
])
def test_plate_engine_normalization_matrix(raw_input, expected_clean, expected_formatted):
    """Validate ANPR normalization and regex parsing across Indian state registration variations."""
    fmt, clean, conf = PlateEngine.validate_and_score(raw_input, 0.95)
    assert clean == expected_clean
    assert fmt == expected_formatted
    assert conf >= 0.90
