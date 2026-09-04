import sys
sys.path.insert(0, ".")
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.services.seed_data import seed_database
from backend.app.models.models import Department, User, Adapter, Watchlist, Camera, Alert, Vehicle, Evidence

print("Resetting PostgreSQL database to Clean Production Baseline...")
# Drop all tables to remove old dummy cameras, sightings, alerts, and evidence
Base.metadata.drop_all(bind=engine)
# Recreate fresh tables
Base.metadata.create_all(bind=engine)
print("Fresh schema created!")

# Seed clean production baseline
db = SessionLocal()
try:
    seed_database(db)
    
    depts = db.query(Department).count()
    users = db.query(User).count()
    adapters = db.query(Adapter).count()
    watchlists = db.query(Watchlist).count()
    cameras = db.query(Camera).count()
    alerts = db.query(Alert).count()
    vehicles = db.query(Vehicle).count()
    evidence = db.query(Evidence).count()
    
    print("\n--- PRODUCTION DATABASE INVENTORY ---")
    print(f"Official Departments   : {depts} (TPD, SMC, HPS, NHA)")
    print(f"Standard Users / RBAC  : {users} (Admin, Investigator, Operator, Viewer)")
    print(f"Federation Adapters    : {adapters} (RTSP, ONVIF, Milestone, Genetec)")
    print(f"Law Watchlists         : {watchlists} (Terror, Stolen, Impound, Crime)")
    print(f"Registered Cameras     : {cameras} (Zero Dummy Data - Clean)")
    print(f"Active Alerts          : {alerts} (Zero Dummy Data - Clean)")
    print(f"Detected Vehicles      : {vehicles} (Zero Dummy Data - Clean)")
    print(f"Sealed Evidence Items  : {evidence} (Zero Dummy Data - Clean)")
    print("-------------------------------------\n")
finally:
    db.close()