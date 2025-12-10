import base64
from typing import Dict, Any
from openai import AsyncOpenAI
from app.services.ocr_service import BaseOCRService
from app.config import settings
import json

class LLMOCRService(BaseOCRService):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-vision-preview"
    
    async def extract_text(self, image_path: str) -> str:
        """Extract text using LLM vision"""
        image_data = self._encode_image(image_path)
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please extract all text from this image. Return only the text content without any additional formatting or explanation."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2048
        )
        
        return response.choices[0].message.content
    
    async def parse_fields(self, raw_text: str, fields: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """Parse fields using LLM"""
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
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )
        
        result_text = response.choices[0].message.content
        
        # Parse JSON from response
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Try to extract JSON if wrapped in markdown
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {}
        
        return result
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')