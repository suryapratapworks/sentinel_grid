import re
import random
from typing import Dict, Any, Tuple

class PlateEngine:
    # Common Indian / Global license plate regex patterns
    PLATE_REGEX = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$"

    @classmethod
    def clean_plate(cls, raw: str) -> str:
        if not raw:
            return ""
        # Remove whitespace, hyphens, dots
        return re.sub(r"[^A-Za-z0-9]", "", raw).upper()

    @classmethod
    def validate_and_score(cls, raw_plate: str, confidence: float = 0.95) -> Tuple[str, str, float]:
        clean = cls.clean_plate(raw_plate)
        formatted = clean
        # Format standard Indian plates:
        # 10 characters (e.g., DL01AB1234 -> DL-01-AB-1234)
        # 9 characters (e.g., UP16Z9999 -> UP-16-Z-9999)
        if len(clean) == 10 and clean[:2].isalpha() and clean[2:4].isdigit() and clean[4:6].isalpha() and clean[6:].isdigit():
            formatted = f"{clean[:2]}-{clean[2:4]}-{clean[4:6]}-{clean[6:]}"
        elif len(clean) == 9 and clean[:2].isalpha() and clean[2:4].isdigit() and clean[4:5].isalpha() and clean[5:].isdigit():
            formatted = f"{clean[:2]}-{clean[2:4]}-{clean[4:5]}-{clean[5:]}"
        elif len(clean) >= 8:
            formatted = clean

        score = max(0.60, min(0.99, confidence))
        return formatted, clean, score

    @classmethod
    def simulate_ocr_read(cls, frame_bytes: bytes = None) -> Dict[str, Any]:
        """Simulates OCR detection with bounding box and high confidence"""
        sample_plates = [
            ("DL-01-AB-1234", "White", "Toyota Fortuner", "SUV"),
            ("MH-02-CD-5678", "Black", "Hyundai Creta", "SUV"),
            ("KA-03-EF-9012", "Silver", "Honda City", "Sedan"),
            ("HR-26-DK-8899", "Red", "Maruti Swift", "Hatchback"),
            ("UP-16-AX-4321", "White", "Mahindra Scorpio", "SUV"),
            ("RJ-14-GH-7788", "Blue", "Tata Nexon", "SUV")
        ]
        chosen = random.choice(sample_plates)
        return {
            "plate_number": chosen[0],
            "normalized_plate": cls.clean_plate(chosen[0]),
            "confidence": round(random.uniform(0.91, 0.99), 2),
            "color": chosen[1],
            "make_model": chosen[2],
            "vehicle_type": chosen[3],
            "bbox": [120, 340, 280, 410]
        }
