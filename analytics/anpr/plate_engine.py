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
