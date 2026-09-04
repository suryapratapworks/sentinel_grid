"""ANPR Worker — runs AI pipeline on phone camera stream.
Posts detections directly to FastAPI backend.
Replaces Kafka with direct HTTP + Redis pub/sub for single-camera use.
"""
import asyncio
import logging
import sys
import os
import requests
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [ANPR-WORKER] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

API_BASE = os.getenv('SENTINEL_API', 'http://localhost:8000/api')
PHONE_IP = os.getenv('PHONE_IP', '192.168.1.100')
PHONE_PORT = os.getenv('PHONE_PORT', '8080')
CAMERA_ID = os.getenv('CAMERA_ID', '')  # set after registering camera
FRAME_SKIP = int(os.getenv('FRAME_SKIP', '10'))

def on_anpr_detection(event: dict):
    """Callback fired by ANPRPipeline for each detected plate."""
    try:
        resp = requests.post(
            f'{API_BASE}/events/simulate_anpr',
            json=event,
            timeout=5
        )
        if resp.status_code == 200:
            result = resp.json()
            status = 'WATCHLIST HIT' if result.get('watchlist_match') else 'Recorded'
            logger.info(f"{status} | Plate: {event['plate_number']} | Conf: {event['confidence']:.2f}")
        else:
            logger.error(f'API error {resp.status_code}: {resp.text}')
    except Exception as e:
        logger.error(f'Failed to post detection: {e}')

def get_or_find_camera() -> tuple[str, str]:
    """Get (camera_id, stream_url) from registry."""
    try:
        resp = requests.get(f'{API_BASE}/cameras', timeout=5)
        cameras = resp.json()
        target_cam = None
        for cam in cameras:
            code = cam.get('camera_code', '').upper()
            vendor = cam.get('vendor', '').upper()
            if 'SAMSUNG' in code or 'PHONE' in code or 'SAMSUNG' in vendor or 'MOBILE' in vendor:
                target_cam = cam
                break
        if not target_cam and cameras:
            target_cam = cameras[0]
            
        if target_cam:
            cam_id = target_cam['id']
            stream_url = f'http://{PHONE_IP}:{PHONE_PORT}/video'
            if target_cam.get('streams') and len(target_cam['streams']) > 0:
                s_url = target_cam['streams'][0].get('stream_url_encrypted', '')
                if '192.168.' in s_url or '10.' in s_url:
                    # Convert RTSP url to HTTP video url for OpenCV performance
                    import re
                    m = re.search(r'(192\.168\.\d+\.\d+):(\d+)', s_url)
                    if m:
                        stream_url = f'http://{m.group(1)}:{m.group(2)}/video'
                    else:
                        stream_url = s_url
            logger.info(f"Found camera: {target_cam['camera_code']} ({cam_id}) -> {stream_url}")
            return cam_id, stream_url
    except Exception as e:
        logger.error(f'Cannot find camera: {e}')
    return '', f'http://{PHONE_IP}:{PHONE_PORT}/video'

def main():
    from ai.pipeline import ANPRPipeline
    
    camera_id, stream_url = get_or_find_camera()
    
    if not camera_id:
        logger.error('No camera found in registry. Register camera first.')
        sys.exit(1)
    
    logger.info(f'Starting ANPR pipeline')
    logger.info(f'  Stream URL: {stream_url}')
    logger.info(f'  Camera ID : {camera_id}')
    logger.info(f'  Frame Skip: every {FRAME_SKIP} frames')
    logger.info(f'  API Base  : {API_BASE}')
    
    pipeline = ANPRPipeline(
        camera_id=camera_id,
        rtsp_url=stream_url,
        on_detection=on_anpr_detection,
        frame_skip=FRAME_SKIP
    )
    
    pipeline.start()
    logger.info('Pipeline running. Press Ctrl+C to stop.')
    
    try:
        while True:
            time.sleep(10)
            stats = pipeline.get_stats()
            logger.info(
                f'Stats: frames={stats["frames_processed"]} | '
                f'detections={stats["detections"]} | '
                f'anpr_events={stats["anpr_events"]} | '
                f'errors={stats["errors"]}'
            )
    except KeyboardInterrupt:
        logger.info('Stopping pipeline...')
        pipeline.stop()

if __name__ == '__main__':
    main()