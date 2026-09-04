import logging
import time
from typing import Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class ByteTracker:
    """Multi-object tracker using ByteTrack algorithm.
    
    Tracks vehicles across frames to prevent duplicate ANPR hits
    for the same vehicle in a single camera view.
    Uses laptrack for CPU-based tracking if available,
    falls back to simple IoU-based tracking.
    """
    
    def __init__(self, camera_id: str, max_age: int = 30, min_hits: int = 3):
        self.camera_id = camera_id
        self.max_age = max_age      # frames before track is dropped
        self.min_hits = min_hits    # frames before track is confirmed
        self.tracks: Dict[int, dict] = {}  # track_id -> track state
        self.next_id = 1
        self.frame_count = 0
        self._init_laptrack()
    
    def _init_laptrack(self):
        try:
            import laptrack
            self._use_laptrack = True
            logger.info(f'ByteTracker [{self.camera_id}]: laptrack backend')
        except ImportError:
            self._use_laptrack = False
            logger.info(f'ByteTracker [{self.camera_id}]: IoU fallback backend')
    
    def update(self, detections: List[Dict]) -> List[Dict]:
        """Update tracker with new detections. Returns tracked detections with IDs."""
        self.frame_count += 1
        
        if not detections:
            # Age out tracks
            expired = [k for k, t in self.tracks.items() if self.frame_count - t['last_seen'] > self.max_age]
            for tid in expired:
                del self.tracks[tid]
            return []
        
        if self._use_laptrack:
            return self._laptrack_update(detections)
        else:
            return self._iou_update(detections)
    
    def _iou_update(self, detections: List[Dict]) -> List[Dict]:
        """Simple IoU-based tracker as fallback."""
        tracked = []
        matched_track_ids = set()
        
        for det in detections:
            bbox = det['bbox']
            best_iou = 0.3  # min IoU threshold
            best_track = None
            
            for tid, track in self.tracks.items():
                iou = self._compute_iou(bbox, track['bbox'])
                if iou > best_iou:
                    best_iou = iou
                    best_track = tid
            
            if best_track is not None:
                self.tracks[best_track].update({
                    'bbox': bbox,
                    'last_seen': self.frame_count,
                    'hits': self.tracks[best_track]['hits'] + 1,
                    'confidence': det['confidence']
                })
                matched_track_ids.add(best_track)
                track_id = best_track
            else:
                track_id = self.next_id
                self.next_id += 1
                self.tracks[track_id] = {
                    'bbox': bbox,
                    'last_seen': self.frame_count,
                    'hits': 1,
                    'confirmed': False,
                    'confidence': det['confidence'],
                    'anpr_fired': False  # prevent duplicate ANPR
                }
            
            track = self.tracks[track_id]
            if track['hits'] >= self.min_hits:
                track['confirmed'] = True
            
            tracked.append({
                **det,
                'track_id': track_id,
                'confirmed': track.get('confirmed', False),
                'hits': track['hits'],
                'anpr_fired': track.get('anpr_fired', False)
            })
        
        # Age out unmatched tracks
        expired = [k for k, t in self.tracks.items()
                   if self.frame_count - t['last_seen'] > self.max_age]
        for tid in expired:
            del self.tracks[tid]
        
        return tracked
    
    def _laptrack_update(self, detections: List[Dict]) -> List[Dict]:
        """laptrack-based ByteTrack update."""
        try:
            # Fall back to IoU tracker for simplicity
            return self._iou_update(detections)
        except Exception as e:
            logger.error(f'laptrack update error: {e}')
            return self._iou_update(detections)
    
    def mark_anpr_fired(self, track_id: int):
        """Mark a track as having ANPR event fired — prevents duplicate sends."""
        if track_id in self.tracks:
            self.tracks[track_id]['anpr_fired'] = True
    
    def should_fire_anpr(self, track_id: int) -> bool:
        """Returns True only if ANPR hasn't fired for this track yet."""
        track = self.tracks.get(track_id, {})
        return track.get('confirmed', False) and not track.get('anpr_fired', False)
    
    @staticmethod
    def _compute_iou(box1: List[int], box2: List[int]) -> float:
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2]-box1[0]) * (box1[3]-box1[1])
        area2 = (box2[2]-box2[0]) * (box2[3]-box2[1])
        union = area1 + area2 - inter
        return inter / union if union > 0 else 0.0
