from pydantic import BaseModel
from typing import Dict, Any, Optional

class FieldConfig(BaseModel):
    name: str
    description: str
    type: str

class OCRRequest(BaseModel):
    file_id: str
    ocr: str
    fields: Dict[str, FieldConfig]

class FileUploadResponse(BaseModel):
    file_id: str

class OCRResponse(BaseModel):
    file_id: str
    ocr: str
    result: Dict[str, Any]
    raw_ocr: str