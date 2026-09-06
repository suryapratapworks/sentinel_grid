import pytest
import asyncio
import uuid
from datetime import datetime, timezone
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.services.seed_data import seed_database
from backend.app.models.models import Watchlist, WatchlistEntry, Vehicle, VehicleSighting, Camera, Department
from analytics.anpr.plate_engine import PlateEngine
from intelligence.watchlist.watchlist_service import WatchlistService
from intelligence.routing.route_service import RouteReconstructionService
from evidence.locker import EvidenceLocker
from federation.adapters.rtsp_adapter import RTSPAdapter

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    yield db
    try:
        from backend.app.models.models import Alert, Evidence, VehicleSighting, Event, Vehicle, WatchlistEntry, CameraStream, Camera
        db.query(Alert).delete(synchronize_session=False)
        db.query(Evidence).delete(synchronize_session=False)
        db.query(VehicleSighting).delete(synchronize_session=False)
        db.query(Event).delete(synchronize_session=False)
        db.query(Vehicle).delete(synchronize_session=False)
        db.query(WatchlistEntry).delete(synchronize_session=False)
        db.query(CameraStream).delete(synchronize_session=False)
        db.query(Camera).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()

def test_plate_normalization():
    raw = "dl-01-ab-1234"
    fmt, clean, conf = PlateEngine.validate_and_score(raw, 0.98)
    assert clean == "DL01AB1234"
    assert fmt == "DL-01-AB-1234"
    assert conf == 0.98

def test_rtsp_tcp_and_exponential_backoff():
    adapter = RTSPAdapter("test-rtsp", "Test Gateway")
    assert adapter.force_tcp is True
    
    delay1 = asyncio.run(adapter.handle_stream_interruption())
    assert delay1 == 2.0
    
    delay2 = asyncio.run(adapter.handle_stream_interruption())
    assert delay2 == 3.0
    
    for _ in range(15):
        asyncio.run(adapter.handle_stream_interruption())
    assert adapter.current_backoff <= 30.0

def test_watchlist_matching(db_session):
    # Setup test watchlist and suspect entry
    wl = db_session.query(Watchlist).first()
    if not wl:
        wl = Watchlist(id=str(uuid.uuid4()), name="Test Watchlist", priority="CRITICAL")
        db_session.add(wl)
        db_session.commit()
    
    entry = WatchlistEntry(
        id=str(uuid.uuid4()),
        watchlist_id=wl.id,
        plate_number="DL-01-AB-1234",
        normalized_plate="DL01AB1234",
        reason="Test Suspect Hit",
        priority="CRITICAL",
        active=True
    )
    db_session.add(entry)
    db_session.commit()

    alert = WatchlistService.check_watchlist_hit(
        db=db_session,
        raw_plate="DL 01 AB 1234",
        camera_id="test-cam-id",
        camera_name="Test CP Camera",
        latitude=28.63,
        longitude=77.21
    )
    assert alert is not None
    assert alert.plate_number == "DL-01-AB-1234"
    assert alert.priority == "CRITICAL"
    assert alert.status == "ACTIVE"

def test_route_reconstruction_chronology(db_session):
    # Create test vehicle and sightings with dynamic identifiers
    suffix = uuid.uuid4().hex[:6].upper()
    dept = db_session.query(Department).first()
    dept_id = dept.id if dept else "dept-tpd"
    
    cam1 = Camera(id=str(uuid.uuid4()), camera_code=f"CAM-TEST-A-{suffix}", name="Test Cam 1", department_id=dept_id, vendor="Axis", protocol="RTSP", codec="H.264", resolution="1080p", fps=25.0, latitude=28.6139, longitude=77.2090, status="ONLINE", integration_type="DIRECT_RTSP")
    cam2 = Camera(id=str(uuid.uuid4()), camera_code=f"CAM-TEST-B-{suffix}", name="Test Cam 2", department_id=dept_id, vendor="Axis", protocol="RTSP", codec="H.264", resolution="1080p", fps=25.0, latitude=28.6328, longitude=77.2195, status="ONLINE", integration_type="DIRECT_RTSP")
    db_session.add_all([cam1, cam2])
    db_session.commit()

    plate = f"HR-26-{suffix[:2]}-{suffix[2:6]}"
    norm_plate = f"HR26{suffix}"
    v = Vehicle(id=str(uuid.uuid4()), plate_number=plate, normalized_plate=norm_plate, vehicle_type="SEDAN", make_model="Honda City", color="White")
    db_session.add(v)
    db_session.commit()

    s1 = VehicleSighting(id=str(uuid.uuid4()), vehicle_id=v.id, camera_id=cam1.id, pts_ms=1000.0, latitude=28.6139, longitude=77.2090, confidence=0.98, speed_kmh=45.0)
    s2 = VehicleSighting(id=str(uuid.uuid4()), vehicle_id=v.id, camera_id=cam2.id, pts_ms=5000.0, latitude=28.6328, longitude=77.2195, confidence=0.97, speed_kmh=52.0)
    db_session.add_all([s1, s2])
    db_session.commit()

    route_data = RouteReconstructionService.reconstruct_route(db_session, norm_plate)
    assert route_data is not None
    assert route_data["total_points"] == 2
    assert route_data["total_distance_km"] > 0
    pts_list = [node["pts_ms"] for node in route_data["route"]]
    assert pts_list == sorted(pts_list)

def test_model_4_evidence_locker_hashing(db_session):
    mock_payload = b"CRITICAL_INCIDENT_EVIDENCE_FRAME_DATA"
    ev = EvidenceLocker.store_evidence(
        db=db_session,
        camera_id="test-cam-01",
        data_bytes=mock_payload,
        evidence_type="SNAPSHOT"
    )
    assert len(ev.hash) == 64
    assert EvidenceLocker.verify_integrity(ev.storage_path, ev.hash) is True