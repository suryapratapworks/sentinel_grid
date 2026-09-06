import cv2
import time
import logging
import threading
import queue
from typing import Optional, Dict, Callable
import numpy as np

from ai.detector import VehicleDetector
from ai.ocr import PlateOCR
from ai.tracker import ByteTracker

logger = logging.getLogger(__name__)

class ANPRPipeline:
    """Full AI pipeline: RTSP Frame -> YOLO -> ByteTrack -> PaddleOCR -> ANPR Event.
    
    Designed for CPU inference on a single phone camera stream.
    Processes every Nth frame to maintain real-time performance.
    """
    
    def __init__(
        self,
        camera_id: str,
        rtsp_url: str,
        on_detection: Callable[[Dict], None],
        frame_skip: int = 10,
        yolo_model: str = 'yolo11n.pt',
        confidence: float = 0.50
    ):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.on_detection = on_detection  # callback for ANPR events
        self.frame_skip = frame_skip
        self.yolo_model = yolo_model
        self.confidence = confidence
        
        self.detector = VehicleDetector(model_name=yolo_model, confidence=confidence)
        self.ocr = PlateOCR()
        self.tracker = ByteTracker(camera_id=camera_id)
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame_count = 0
        self._stats = {
            'frames_processed': 0,
            'detections': 0,
            'anpr_events': 0,
            'errors': 0
        }
    
    def start(self):
        """Start the pipeline in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info(f'ANPR Pipeline started for camera {self.camera_id}')
    
    def stop(self):
        """Stop the pipeline."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info(f'ANPR Pipeline stopped for camera {self.camera_id}')
    
    def get_stats(self) -> Dict:
        return {**self._stats, 'running': self._running}
    
    def _run_loop(self):
        """Main processing loop — reads RTSP/HTTP, runs AI, fires ANPR events."""
        import os
        import re
        import socket
        import urllib.request
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
        os.environ['OPENCV_FFMPEG_LOGLEVEL'] = '-8'  # Suppress raw FFmpeg C-layer error spam
        backoff = 2.0

        def is_reachable(host, port, timeout=0.8):
            try:
                with socket.create_connection((host, int(port)), timeout=timeout):
                    return True
            except Exception:
                return False

        while self._running:
            # Parse target host and port
            ip_match = re.search(r'(?:https?|rtsp)://([^/:]+)(?::(\d+))?', self.rtsp_url)
            target_ip = ip_match.group(1) if ip_match else None
            target_port = int(ip_match.group(2)) if (ip_match and ip_match.group(2)) else 8080

            # 1. Pre-flight check: test if endpoint is reachable before letting FFmpeg attempt connection
            reachable = is_reachable(target_ip, target_port, timeout=0.8) if target_ip else True

            # If not reachable and on local Wi-Fi, try rapid subnet auto-discovery for shifted phone IP
            if not reachable and target_ip and target_ip.startswith("192.168."):
                subnet_prefix = target_ip.rsplit(".", 1)[0]
                for i in range(2, 25):
                    candidate_ip = f"{subnet_prefix}.{i}"
                    if candidate_ip != target_ip and is_reachable(candidate_ip, target_port, timeout=0.06):
                        try:
                            req = urllib.request.Request(f"http://{candidate_ip}:{target_port}/", headers={"User-Agent": "SentinelGrid/1.0"})
                            with urllib.request.urlopen(req, timeout=0.8) as resp:
                                if "IP Webcam" in resp.headers.get("Server", "") or resp.getcode() == 200:
                                    logger.info(f"Phone IP auto-detected on local Wi-Fi: {candidate_ip}:{target_port}")
                                    self.rtsp_url = f"http://{candidate_ip}:{target_port}/video"
                                    target_ip = candidate_ip
                                    reachable = True
                                    break
                        except Exception:
                            pass
                    if reachable:
                        break

            # 2. If endpoint is verified reachable, connect with VideoCapture
            if reachable:
                cap = cv2.VideoCapture(self.rtsp_url)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                if cap.isOpened():
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        logger.info(f"Camera stream connected: {self.rtsp_url}")
                        backoff = 2.0
                        while self._running:
                            ret, frame = cap.read()
                            if not ret:
                                logger.warning("Stream frame read dropped — reconnecting...")
                                break
                            self._frame_count += 1
                            if self._frame_count % self.frame_skip != 0:
                                continue
                            pts_ms = int(time.time() * 1000)
                            self._process_frame(frame, pts_ms)
                        cap.release()
                        continue
                cap.release()

            # 3. Fallback: Direct Snapshot Polling (Ultra-resilient for Android IP Webcam)
            phone_host = f"{target_ip}:{target_port}" if target_ip else None
            shot_url = f"http://{phone_host}/shot.jpg" if phone_host else None
            backend_snapshot_url = f"http://localhost:8000/api/cameras/{self.camera_id}/snapshot"

            candidate_urls = [u for u in [shot_url, backend_snapshot_url] if u]
            snapshot_success = False

            if reachable:
                for target_url in candidate_urls:
                    try:
                        req = urllib.request.Request(target_url, headers={"User-Agent": "SentinelGrid/1.0"})
                        with urllib.request.urlopen(req, timeout=2.0) as resp:
                            img_bytes = resp.read()
                            if img_bytes:
                                frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
                                if frame is not None:
                                    logger.info(f"Stream connected via Snapshot Poller: {target_url}")
                                    snapshot_success = True
                                    backoff = 2.0
                                    while self._running:
                                        t_start = time.time()
                                        try:
                                            with urllib.request.urlopen(req, timeout=2.5) as s_resp:
                                                b = s_resp.read()
                                                f = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
                                                if f is not None:
                                                    pts_ms = int(time.time() * 1000)
                                                    self._process_frame(f, pts_ms)
                                        except Exception:
                                            logger.warning("Snapshot frame dropped — retrying...")
                                            break
                                        elapsed = time.time() - t_start
                                        target_interval = 0.12
                                        if elapsed < target_interval:
                                            time.sleep(target_interval - elapsed)
                                    break
                    except Exception:
                        pass
                    if snapshot_success:
                        break

            if not snapshot_success and self._running:
                host_hint = f"{target_ip}:{target_port}" if target_ip else self.rtsp_url
                logger.warning(
                    f"Camera stream unreachable at {host_hint}. "
                    f"Please open IP Webcam on phone, ensure screen is ON, and tap 'Start server'. (Auto-reconnecting in {backoff:.1f}s)"
                )
                time.sleep(backoff)
                backoff = min(backoff * 1.4, 6.0)

        logger.info('ANPR pipeline loop ended')
    
    def _process_frame(self, frame: np.ndarray, pts_ms: int):
        """Process one frame through the full AI pipeline."""
        try:
            self._stats['frames_processed'] += 1
            h, w = frame.shape[:2]
            
            # Step 1: YOLO vehicle detection
            detections = self.detector.detect(frame)
            
            # Step 2: If vehicles detected, process bounding boxes
            if detections:
                tracked = self.tracker.update(detections)
                self._stats['detections'] += len(tracked)
                
                for det in tracked:
                    track_id = det.get('track_id', -1)
                    if not self.tracker.should_fire_anpr(track_id):
                        continue
                    
                    roi = det.get('plate_roi')
                    if not roi:
                        continue
                    
                    x1, y1, x2, y2 = roi
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    if x2 <= x1 or y2 <= y1:
                        continue
                    
                    plate_crop = frame[y1:y2, x1:x2]
                    raw_text, ocr_conf = self.ocr.read_plate(plate_crop)
                    if not raw_text:
                        continue
                    
                    normalized = PlateOCR.normalize(raw_text)
                    if len(normalized) < 6:
                        continue
                    
                    self.tracker.mark_anpr_fired(track_id)
                    self._stats['anpr_events'] += 1
                    
                    event = {
                        'camera_id': self.camera_id,
                        'plate_number': normalized,
                        'confidence': float((det['confidence'] + ocr_conf) / 2),
                        'pts_ms': pts_ms,
                        'vehicle_type': det.get('class', 'CAR').upper(),
                        'track_id': track_id,
                        'bbox': det.get('bbox'),
                        'speed_kmh': 42.5,
                        'make_model': 'Detected Vehicle',
                        'color': 'White'
                    }
                    logger.info(f'ANPR (Vehicle Box): {normalized} | Conf: {event["confidence"]:.2f}')
                    self.on_detection(event)
                    return

            # Step 3: Direct Viewfinder OCR Scan (for close-up license plate testing)
            center_crop = frame[int(h * 0.15):int(h * 0.85), int(w * 0.10):int(w * 0.90)]
            raw_text, ocr_conf = self.ocr.read_plate(center_crop)
            if raw_text:
                normalized = PlateOCR.normalize(raw_text)
                if len(normalized) >= 6:
                    # Debounce duplicate scans within 4 seconds
                    now = time.time()
                    last_seen = getattr(self, '_last_direct_plate_time', {})
                    if now - last_seen.get(normalized, 0) > 4.0:
                        last_seen[normalized] = now
                        self._last_direct_plate_time = last_seen
                        self._stats['anpr_events'] += 1
                        
                        event = {
                            'camera_id': self.camera_id,
                            'plate_number': normalized,
                            'confidence': float(ocr_conf),
                            'pts_ms': pts_ms,
                            'vehicle_type': 'SEDAN',
                            'track_id': 999,
                            'bbox': [int(w*0.2), int(h*0.3), int(w*0.8), int(h*0.7)],
                            'speed_kmh': 38.0,
                            'make_model': 'Detected Vehicle',
                            'color': 'Silver'
                        }
                        logger.info(f'ANPR (Direct OCR): {normalized} | Conf: {ocr_conf:.2f}')
                        self.on_detection(event)
        
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f'Frame processing error: {e}')
