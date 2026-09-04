import os
import time
import logging
from typing import List, Dict, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class VehicleDetector:
    """YOLOv8/YOLO11 vehicle detector — CPU inference.
    
    Detects vehicles and license plate regions from video frames.
    Falls back to mock detections if YOLO model is unavailable.
    """
    
    def __init__(self, model_name: str = 'yolo11n.pt', confidence: float = 0.50):
        self.model_name = model_name
        self.confidence = confidence
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            from ultralytics import YOLO
            model_path = os.path.join(os.path.dirname(__file__), 'models', self.model_name)
            if not os.path.exists(model_path):
                # Auto-download to models dir
                os.makedirs(os.path.join(os.path.dirname(__file__), 'models'), exist_ok=True)
                self.model = YOLO(self.model_name)  # Downloads from ultralytics hub
                self.model.save(model_path)
            else:
                self.model = YOLO(model_path)
            logger.info(f'YOLO model loaded: {self.model_name} (CPU)')
        except ImportError:
            logger.warning('ultralytics not installed — using mock detector')
        except Exception as e:
            logger.warning(f'YOLO load error: {e} — using mock detector')
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """Detect vehicles in a frame. Returns list of detection dicts."""
        if self.model is None:
            return self._mock_detections(frame)
        
        try:
            results = self.model(frame, conf=self.confidence, classes=[2, 3, 5, 7], verbose=False)
            # YOLO classes: 2=car, 3=motorbike, 5=bus, 7=truck
            detections = []
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_names = {2: 'car', 3: 'motorbike', 5: 'bus', 7: 'truck'}
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'class': class_names.get(cls, 'vehicle'),
                        'confidence': conf,
                        'plate_roi': self._estimate_plate_roi(x1, y1, x2, y2, cls)
                    })
            return detections
        except Exception as e:
            logger.error(f'Detection error: {e}')
            return self._mock_detections(frame)
    
    def _estimate_plate_roi(self, x1, y1, x2, y2, cls) -> List[int]:
        """Estimate where the license plate region is within the vehicle bbox."""
        h = y2 - y1
        w = x2 - x1
        # Plate is typically at bottom 20-30% of vehicle, centered
        plate_y1 = y1 + int(h * 0.70)
        plate_y2 = y2 - int(h * 0.05)
        plate_x1 = x1 + int(w * 0.15)
        plate_x2 = x2 - int(w * 0.15)
        return [plate_x1, plate_y1, plate_x2, plate_y2]
    
    def _mock_detections(self, frame: np.ndarray) -> List[Dict]:
        """Mock detections for testing without a real YOLO model."""
        if frame is None or frame.size == 0:
            return []
        h, w = frame.shape[:2]
        return [{
            'bbox': [int(w*0.2), int(h*0.3), int(w*0.8), int(h*0.8)],
            'class': 'car',
            'confidence': 0.88,
            'plate_roi': [int(w*0.3), int(h*0.65), int(w*0.7), int(h*0.78)]
        }]
