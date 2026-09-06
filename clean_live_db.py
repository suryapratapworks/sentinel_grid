import sys
sys.path.insert(0, ".")
from backend.app.core.database import SessionLocal
from backend.app.models.models import Camera, CameraStream, Event, Alert, Vehicle, VehicleSighting, Evidence, WatchlistEntry

db = SessionLocal()
try:
    db.query(Alert).delete()
    db.query(Evidence).delete()
    db.query(VehicleSighting).delete()
    db.query(Event).delete()
    db.query(Vehicle).delete()
    db.query(WatchlistEntry).delete()
    db.query(CameraStream).delete()
    db.query(Camera).delete()
    db.commit()
    print("Live Database Cleaned: 0 Cameras, 0 Alerts, 0 Sightings, 0 Events, 0 Vehicles, 0 Evidence.")
finally:
    db.close()