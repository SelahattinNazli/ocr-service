import easyocr
from typing import Dict, Any
from app.services.ocr_service import BaseOCRService
from pdf2image import convert_from_path
import tempfile
import os
import re


class EasyOCRService(BaseOCRService):
    def __init__(self):
        self.reader = easyocr.Reader(["tr", "en"], gpu=False)

    async def extract_text(self, image_path: str) -> str:
        """Extract text using EasyOCR"""

        # If PDF → convert to image first
        if image_path.endswith(".pdf"):
            images = convert_from_path(image_path)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                images[0].save(tmp.name, "PNG")
                image_path = tmp.name

        result = self.reader.readtext(image_path)
        text = "\n".join([detection[1] for detection in result])

        # Delete temp file
        if image_path.endswith(".png") and "tmp" in image_path:
            try:
                os.remove(image_path)
            except Exception:
                pass

        return text

    async def parse_fields(
        self, raw_text: str, fields: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """Parse fields from extracted text"""
        result = {}

        for field_key, field_config in fields.items():
            field_name = field_config["name"]
            field_desc = field_config["description"]
            field_type = field_config["type"]

            value = self._extract_field_value(
                raw_text, field_name, field_desc, field_type
            )
            result[field_key] = value

        return result

    def _extract_field_value(
        self, text: str, name: str, description: str, field_type: str
    ) -> Any:
        """Extract field value using pattern matching"""

        # Clean entire text by removing spaces and newlines
        text_clean = text.replace(" ", "").replace("\n", "")

        # For Tax Number
        if "vergi" in name.lower():
            numbers = re.findall(r"\d{11}", text_clean)
            if numbers:
                return int(numbers[0]) if field_type == "integer" else numbers[0]

        # Generic number extraction
        if field_type == "integer":
            numbers = re.findall(r"\d+", text_clean)
            return int(numbers[0]) if numbers else None

        # Generic string extraction
        lines = text.split("\n")
        for line in lines:
            if name.lower() in line.lower():
                return line.strip()

        return None
