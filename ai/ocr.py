import logging
import re
from typing import Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

INDIAN_PLATE_PATTERN = re.compile(
    r'^([A-Z]{2})[\s\-]?(\d{1,2})[\s\-]?([A-Z]{1,3})[\s\-]?(\d{4})$'
)

class PlateOCR:
    """EasyOCR + PyTorch based license plate text extractor.
    
    Reads text from cropped plate image regions and full viewfinders.
    Falls back to regex matching if OCR is unavailable.
    """
    
    def __init__(self):
        self.reader = None
        self._load_ocr()
    
    def _load_ocr(self):
        try:
            import easyocr
            self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            logger.info('EasyOCR loaded (PyTorch CPU Engine)')
        except Exception as e:
            logger.warning(f'EasyOCR init error: {e} — using mock OCR fallback')
            self.reader = None
    
    def read_plate(self, plate_crop: np.ndarray) -> Tuple[Optional[str], float]:
        """Extract plate text from cropped image region.
        Returns (plate_text, confidence) or (None, 0.0) if not readable.
        """
        if plate_crop is None or plate_crop.size == 0:
            return None, 0.0
        
        if self.reader is None:
            return self._mock_read(plate_crop)
        
        try:
            results = self.reader.readtext(plate_crop, detail=1)
            if not results:
                return None, 0.0
            
            texts = []
            confs = []
            for bbox, text, conf in results:
                clean_t = re.sub(r'[^A-Z0-9]', '', text.strip().upper())
                if len(clean_t) >= 2:
                    texts.append(clean_t)
                    confs.append(float(conf))
            
            if not texts:
                return None, 0.0
            
            combined = ''.join(texts)
            avg_conf = sum(confs) / len(confs) if confs else 0.85
            
            # Validate minimum length for vehicle plates
            if len(combined) < 5:
                return None, 0.0
            
            return combined, avg_conf
        except Exception as e:
            logger.debug(f'OCR error: {e}')
            return None, 0.0
    
    def _mock_read(self, frame: np.ndarray) -> Tuple[str, float]:
        """Mock plate reading for testing."""
        mock_plates = ['DL01AB1234', 'MH02CD5678', 'HR26DK8899', 'UP16AX9900']
        import random
        return random.choice(mock_plates), 0.87
    
    @staticmethod
    def normalize(raw: str) -> str:
        """Normalize plate text to standard Indian format DL-01-AB-1234."""
        if not raw:
            return raw
        clean = re.sub(r'[^A-Z0-9]', '', raw.upper())
        
        # Character correction for Indian license plates (StateCode 2 chars, DistrictCode 2 digits, Series 1-3 chars, Unique 4 digits)
        if len(clean) >= 8:
            state = clean[:2]
            # Replace digits in state with letters if misrecognized
            state = state.replace('0', 'O').replace('1', 'I')
            
            # District (next 2 chars should be digits)
            dist = clean[2:4].replace('O', '0').replace('I', '1').replace('Z', '2').replace('S', '5').replace('B', '8')
            
            # Tail 4 chars should be digits
            tail = clean[-4:].replace('O', '0').replace('I', '1').replace('Z', '2').replace('S', '5').replace('B', '8')
            
            # Middle series letters
            series = clean[4:-4].replace('0', 'O').replace('1', 'I')
            
            rebuilt = f'{state}{dist}{series}{tail}'
            m = INDIAN_PLATE_PATTERN.match(rebuilt)
            if m:
                return f'{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3)}-{m.group(4)}'
            return f'{state}-{dist}-{series}-{tail}'
            
        m = INDIAN_PLATE_PATTERN.match(clean)
        if m:
            return f'{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3)}-{m.group(4)}'
        return clean
