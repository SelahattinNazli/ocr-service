import base64
import httpx
from typing import Dict, Any
from app.services.ocr_service import BaseOCRService
from app.config import settings
import json


class LLMOCRService(BaseOCRService):
    def __init__(self):
        self.api_url = settings.OLLAMA_API_URL
        self.model = settings.OLLAMA_MODEL

    async def extract_text(self, image_path: str) -> str:
        """Extract text using Ollama"""
        image_data = self._encode_image(image_path)

        prompt = "Please extract all text from this image. Return only the text content without any additional formatting or explanation."

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/generate",
                json=payload,
                timeout=300.0,
            )

        result = response.json()
        return result.get("response", "")

    async def parse_fields(
        self, raw_text: str, fields: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """Parse fields using Ollama"""
        fields_description = json.dumps(fields, ensure_ascii=False, indent=2)

        prompt = f"""Analyze the following extracted text and extract the requested fields.

Extracted Text:
{raw_text}

Fields to Extract:
{fields_description}

Return the result as a valid JSON object with field keys as keys and extracted values as values.
Respect the 'type' field when extracting (convert to integer if type is 'integer').
If a field cannot be found, use null value.

Return only valid JSON, no additional text."""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/generate",
                json=payload,
                timeout=300.0,
            )

        result_text = response.json().get("response", "{}")

        # Parse JSON from response
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Try to extract JSON if wrapped in markdown
            import re

            json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {}

        return result

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
