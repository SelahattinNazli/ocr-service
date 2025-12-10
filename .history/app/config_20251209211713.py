from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OLLAMA_API_URL: str = ""
    OLLAMA_MODEL: str = ""
    UPLOAD_DIR: str = "./app/uploads"
    MAX_FILE_SIZE: int = 10485760

    # IMPORTANT: type=str olmalı
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf"

    DEBUG: bool = False

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    def split_extensions(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v

    class Config:
        env_file = ".env"
