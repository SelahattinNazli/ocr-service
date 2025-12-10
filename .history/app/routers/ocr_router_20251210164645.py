import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.schemas import FileUploadResponse, OCRRequest, OCRResponse
from app.config import settings
from app.services.easyocr_service import EasyOCRService
from app.services.llm_ocr_service import LLMOCRService

router = APIRouter()

# Initialize services
easyocr_service = EasyOCRService()
llm_ocr_service = LLMOCRService()


@router.post("/file-upload")
async def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    """Upload a file and get a unique file ID"""

    # Validate file extension
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension .{file_ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Create file path
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{file_id}.{file_ext}"

    # Save file
    try:
        contents = await file.read()

        # Check file size
        if len(contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE} bytes",
            )

        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    return FileUploadResponse(file_id=file_id)


@router.post("/ocr")
async def perform_ocr(request: OCRRequest) -> OCRResponse:
    """Perform OCR on uploaded file and extract specified fields"""

    # Validate OCR method
    if request.ocr not in ["easyocr", "llm_ocr"]:
        raise HTTPException(
            status_code=400, detail="OCR method must be 'easyocr' or 'llm_ocr'"
        )

    # Find file
    upload_dir = Path(settings.UPLOAD_DIR)
    file_path = None

    for file in upload_dir.glob(f"{request.file_id}.*"):
        file_path = file
        break

    if not file_path or not file_path.exists():
        raise HTTPException(
            status_code=404, detail=f"File with ID {request.file_id} not found"
        )

    try:
        # Convert Pydantic models to dict
        fields_dict = {k: v.model_dump() for k, v in request.fields.items()}

        # For both methods, first extract text using EasyOCR
        raw_ocr = await easyocr_service.extract_text(str(file_path))

        # Then parse fields based on selected method
        if request.ocr == "easyocr":
            # Use EasyOCR's built-in parsing
            parsed_result = await easyocr_service.parse_fields(raw_ocr, fields_dict)
        else:
            # Use LLM (Ollama Gemma3) for field parsing
            parsed_result = await llm_ocr_service.parse_fields(raw_ocr, fields_dict)

        return OCRResponse(
            file_id=request.file_id,
            ocr=request.ocr,
            result=parsed_result,
            raw_ocr=raw_ocr,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
