import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.models import (
    Department, User, Adapter, Watchlist
)
from backend.app.core.security import get_password_hash

def seed_database(db: Session):
    """
    Production-grade database initialization.
    Initializes core departments, system adapters, administrative accounts,
    and law-enforcement watchlist schemas without inserting dummy cameras or fake events.
    """
    if db.query(Department).first():
        return

    print("Initializing SENTINEL GRID Production Baseline...")

    # 1. Official Government Departments
    dept_traffic = Department(
        id=str(uuid.uuid4()),
        name="State Traffic Police Division",
        code="TPD",
        contact_information="traffic-ops@state.gov",
        created_at=datetime.now(timezone.utc)
    )
    dept_municipal = Department(
        id=str(uuid.uuid4()),
        name="Smart City Municipal Corporation",
        code="SMC",
        contact_information="smartcity-cctv@municipal.gov",
        created_at=datetime.now(timezone.utc)
    )
    dept_security = Department(
        id=str(uuid.uuid4()),
        name="State Homeland & Public Safety",
        code="HPS",
        contact_information="homeland-intel@state.gov",
        created_at=datetime.now(timezone.utc)
    )
    dept_highway = Department(
        id=str(uuid.uuid4()),
        name="National Highways Authority (NHAI)",
        code="NHA",
        contact_information="highways-toll@nhai.gov",
        created_at=datetime.now(timezone.utc)
    )

    db.add_all([dept_traffic, dept_municipal, dept_security, dept_highway])
    db.commit()

    # 2. Production Roles & Standard Operating Accounts
    user_admin = User(
        id=str(uuid.uuid4()),
        username="admin",
        email="admin@sentinelgrid.gov",
        password_hash=get_password_hash("admin123"),
        role_name="SUPER_ADMIN",
        department_id=dept_security.id,
        created_at=datetime.now(timezone.utc)
    )
    user_investigator = User(
        id=str(uuid.uuid4()),
        username="investigator",
        email="investigator@police.gov",
        password_hash=get_password_hash("investigator123"),
        role_name="INVESTIGATOR",
        department_id=dept_traffic.id,
        created_at=datetime.now(timezone.utc)
    )
    user_operator = User(
        id=str(uuid.uuid4()),
        username="operator",
        email="operator@traffic.gov",
        password_hash=get_password_hash("operator123"),
        role_name="TRAFFIC_OPERATOR",
        department_id=dept_traffic.id,
        created_at=datetime.now(timezone.utc)
    )
    user_viewer = User(
        id=str(uuid.uuid4()),
        username="municipal_viewer",
        email="viewer@municipal.gov",
        password_hash=get_password_hash("viewer123"),
        role_name="MUNICIPAL_VIEWER",
        department_id=dept_municipal.id,
        created_at=datetime.now(timezone.utc)
    )

    db.add_all([user_admin, user_investigator, user_operator, user_viewer])
    db.commit()

    # 3. Federation Model Adapters
    adapter_rtsp = Adapter(
        id=str(uuid.uuid4()),
        name="Core RTSP/TCP Stream Gateway",
        adapter_type="RTSP",
        vendor="Direct RTSP/TCP Bridge",
        version="2.4.1",
        status="ONLINE",
        event_throughput_fps=0.0,
        connected_systems_count=0,
        created_at=datetime.now(timezone.utc)
    )
    adapter_onvif = Adapter(
        id=str(uuid.uuid4()),
        name="ONVIF Profile S/T Discovery Connector",
        adapter_type="ONVIF",
        vendor="ONVIF Core Consortium",
        version="1.8.0",
        status="ONLINE",
        event_throughput_fps=0.0,
        connected_systems_count=0,
        created_at=datetime.now(timezone.utc)
    )
    adapter_milestone = Adapter(
        id=str(uuid.uuid4()),
        name="Milestone XProtect Federation Bridge",
        adapter_type="PROPRIETARY_VMS",
        vendor="Milestone Systems",
        version="3.2.0",
        status="ONLINE",
        event_throughput_fps=0.0,
        connected_systems_count=0,
        created_at=datetime.now(timezone.utc)
    )
    adapter_genetec = Adapter(
        id=str(uuid.uuid4()),
        name="Genetec Security Center Middleware",
        adapter_type="PROPRIETARY_VMS",
        vendor="Genetec Inc.",
        version="5.11.2",
        status="ONLINE",
        event_throughput_fps=0.0,
        connected_systems_count=0,
        created_at=datetime.now(timezone.utc)
    )
    db.add_all([adapter_rtsp, adapter_onvif, adapter_milestone, adapter_genetec])
    db.commit()

    # 4. Official Law Enforcement Watchlists (clean & ready for active entries)
    wl_terror = Watchlist(
        id=str(uuid.uuid4()),
        name="National Security & Counter-Terrorism Priority Hotlist",
        description="High-priority surveillance hotlist for anti-terror and homeland security targets.",
        priority="CRITICAL",
        created_at=datetime.now(timezone.utc)
    )
    wl_stolen = Watchlist(
        id=str(uuid.uuid4()),
        name="Stolen Vehicle Automated Intercept Hotlist",
        description="Vehicles reported stolen, hijacked, or involved in active felony pursuits.",
        priority="HIGH",
        created_at=datetime.now(timezone.utc)
    )
    wl_impound = Watchlist(
        id=str(uuid.uuid4()),
        name="Traffic Impound & High-Risk Violators List",
        description="Vehicles with suspended registration, repeated red-light violations, or court impound orders.",
        priority="MEDIUM",
        created_at=datetime.now(timezone.utc)
    )
    wl_crime = Watchlist(
        id=str(uuid.uuid4()),
        name="Organized Crime & Narcotics Investigation Watchlist",
        description="Target vehicles flagged under active criminal court warrants or narcotics surveillance.",
        priority="HIGH",
        created_at=datetime.now(timezone.utc)
    )
    db.add_all([wl_terror, wl_stolen, wl_impound, wl_crime])
    db.commit()

    print("SENTINEL GRID Production Baseline Initialized: Clean state ready for real cameras and detections.")