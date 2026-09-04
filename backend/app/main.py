import asyncio
import logging
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.database import engine, Base
from backend.app.services.seed_data import seed_database
from backend.app.api import (
    auth, cameras, ingest, events, vehicles,
    watchlists, alerts, evidence, federation, dashboard
)
from backend.app.api import streams
from backend.app.api import websocket as ws_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("SENTINEL GRID starting up...")
    Base.metadata.create_all(bind=engine)
    from backend.app.core.database import SessionLocal
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # Initialize Redis
    try:
        from backend.app.core.redis_client import get_redis
        r = await get_redis()
        await r.set("sentinel:startup", datetime.now(timezone.utc).isoformat())
        logger.info("Redis: OK (fakeredis in-process)")
    except Exception as e:
        logger.warning(f"Redis startup warning: {e}")

    logger.info("SENTINEL GRID ready. Listening on :8000")
    yield

    # Shutdown
    logger.info("SENTINEL GRID shutting down...")

app = FastAPI(
    title="SENTINEL GRID - Unified Federated Video Intelligence",
    description="Production-grade CCTV integration and intelligence platform",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core API routers
app.include_router(auth.router,        prefix="/api")
app.include_router(cameras.router,     prefix="/api")
app.include_router(ingest.router,      prefix="/api")
app.include_router(events.router,      prefix="/api")
app.include_router(vehicles.router,    prefix="/api")
app.include_router(watchlists.router,  prefix="/api")
app.include_router(alerts.router,      prefix="/api")
app.include_router(evidence.router,    prefix="/api")
app.include_router(federation.router,  prefix="/api")
app.include_router(dashboard.router,   prefix="/api")

# Production additions
app.include_router(streams.router,     prefix="/api")
from backend.app.api import spatial
app.include_router(spatial.router,     prefix="/api")
app.include_router(ws_router.router)

@app.get("/health")
async def health():
    return {
        "status": "operational",
        "version": "2.0.0",
        "components": {
            "api": "ok",
            "database": "ok",
            "redis": "fakeredis",
            "mediamtx": "check /api/streams/mediamtx/status",
            "ai_engine": "check workers/anpr_worker.py"
        }
    }