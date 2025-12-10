import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    UPLOAD_DIR: str = "./app/uploads"
    MAX_FILE_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: list = ["jpg", "jpeg", "png", "pdf"]
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)