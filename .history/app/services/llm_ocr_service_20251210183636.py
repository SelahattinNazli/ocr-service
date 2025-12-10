import json
import re
import httpx
from typing import Dict, Any
from app.services.ocr_service import BaseOCRService
from app.config import settings


class LLMOCRService(BaseOCRService):
    def __init__(self):
        self.api_url = settings.OLLAMA_API_URL
        self.model = settings.OLLAMA_MODEL

    async def extract_text(self, image_path: str) -> str:
        """Extract text - delegated to EasyOCR"""
        # LLM-based OCR uses EasyOCR's extracted text
        # This method is not used in practice for text extraction
        return ""

    async def parse_fields(
        self, raw_text: str, fields: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """Parse fields using Ollama Gemma3"""
        fields_description = json.dumps(fields, ensure_ascii=False, indent=2)

        prompt = f"""Analyze the following extracted text and extract the requested fields.

        Extracted Text:
        {raw_text}

        Fields to Extract:
        {fields_description}

        IMPORTANT: 
        - Extract values EXACTLY as they appear in the text
        - For numbers, include ALL digits, do not skip or truncate
        - Return as a valid JSON object
        - Use field keys as keys and extracted values as values
        - If type is 'integer', convert the complete number to integer
        - If a field cannot be found, use null value

        Return ONLY valid JSON, no additional text or explanation."""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/generate",
                    json=payload,
                )

            result_text = response.json().get("response", "{}")

            # Parse JSON from response
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # Try to extract JSON if wrapped in markdown
                json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        result = {}
                else:
                    result = {}

            return result
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
