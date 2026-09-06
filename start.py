"""
SENTINEL GRID — Production Startup Orchestrator
Replaces Docker Compose for native Windows operation.

Usage:
    python start.py              # Start all services
    python start.py --no-ai      # Skip AI worker (no camera connected)
    python start.py --no-mediamtx  # Skip MediaMTX

Services started:
    1. MediaMTX   - RTSP -> HLS/WebRTC relay  (:8554, :8888, :8889)
    2. Backend     - FastAPI + WebSocket        (:8000)
    3. Frontend    - Vite dev server            (:3000)
    4. ANPR Worker - AI pipeline               (background)
"""
import subprocess
import sys
import os
import time
import signal
import threading
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
BINS = os.path.join(ROOT, "bins")
MEDIAMTX_EXE = os.path.join(BINS, "mediamtx", "mediamtx.exe")
MEDIAMTX_CONF = os.path.join(ROOT, "mediamtx", "mediamtx.yml")
FRONTEND_DIR = os.path.join(ROOT, "frontend")

processes = []

def log(service, msg):
    print(f"[{service:12s}] {msg}")

def start_mediamtx():
    if not os.path.exists(MEDIAMTX_EXE):
        log("MediaMTX", "Binary not found at bins/mediamtx/mediamtx.exe — skipping")
        return None
    log("MediaMTX", f"Starting RTSP->HLS/WebRTC relay...")
    proc = subprocess.Popen(
        [MEDIAMTX_EXE, MEDIAMTX_CONF],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=ROOT
    )
    processes.append(proc)
    time.sleep(1)
    if proc.poll() is None:
        log("MediaMTX", "Running  -> HLS: http://localhost:8888  WebRTC: http://localhost:8889")
    return proc

def start_backend():
    log("Backend", "Starting FastAPI server...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"],
        cwd=ROOT
    )
    processes.append(proc)
    time.sleep(2)
    log("Backend", "Running  -> http://localhost:8000  Docs: http://localhost:8000/docs")
    return proc

def start_frontend():
    npm = "npm.cmd" if os.name == "nt" else "npm"
    log("Frontend", "Starting Vite dev server...")
    proc = subprocess.Popen(
        [npm, "run", "dev"],
        cwd=FRONTEND_DIR
    )
    processes.append(proc)
    time.sleep(3)
    log("Frontend", "Running  -> http://localhost:3000")
    return proc

def start_anpr_worker(phone_ip="192.168.1.100"):
    log("ANPR-AI", f"Starting AI pipeline for phone at {phone_ip}...")
    env = os.environ.copy()
    env["PHONE_IP"] = phone_ip
    proc = subprocess.Popen(
        [sys.executable, "workers/anpr_worker.py"],
        cwd=ROOT, env=env
    )
    processes.append(proc)
    log("ANPR-AI", "AI Pipeline running (YOLO11 + PaddleOCR + ByteTrack)")
    return proc

def cleanup(signum=None, frame=None):
    log("System", "Shutting down all services...")
    for proc in processes:
        try:
            proc.terminate()
        except Exception:
            pass
    time.sleep(1)
    for proc in processes:
        try:
            proc.kill()
        except Exception:
            pass
    log("System", "All services stopped.")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="SENTINEL GRID Production Launcher")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI ANPR worker")
    parser.add_argument("--no-mediamtx", action="store_true", help="Skip MediaMTX")
    parser.add_argument("--phone-ip", default="192.168.1.100", help="Phone camera IP")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("\n" + "="*60)
    print("  SENTINEL GRID v2.0 — Production Stack")
    print("="*60)

    if not args.no_mediamtx:
        start_mediamtx()

    start_backend()
    start_frontend()

    if not args.no_ai:
        time.sleep(3)  # Wait for backend to be ready
        start_anpr_worker(args.phone_ip)

    print("\n" + "="*60)
    print("  All services running. Press Ctrl+C to stop all.")
    print("="*60)
    print(f"  UI        : http://localhost:3000")
    print(f"  API       : http://localhost:8000")
    print(f"  API Docs  : http://localhost:8000/docs")
    print(f"  HLS       : http://localhost:8888/phone_cam/index.m3u8")
    print(f"  WebSocket : ws://localhost:8000/ws/alerts")
    print("="*60 + "\n")

    # Keep alive
    try:
        while True:
            time.sleep(5)
            for p in list(processes):
                if p.poll() is not None:
                    log("System", f"Process {p.pid} exited with code {p.returncode}")
                    processes.remove(p)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()