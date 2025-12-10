from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from PIL import Image
import pytesseract


class BaseOCRService(ABC):
    @abstractmethod
    async def extract_text(self, image_path: str) -> str:
        """Extract raw text from image"""
        pass

    @abstractmethod
    async def parse_fields(
        self, raw_text: str, fields: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """Parse specific fields from raw text"""
        pass
