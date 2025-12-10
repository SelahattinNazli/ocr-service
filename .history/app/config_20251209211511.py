from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OLLAMA_API_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:4b"

    UPLOAD_DIR: str = "./app/uploads"
    MAX_FILE_SIZE: int = 10485760

    ALLOWED_EXTENSIONS: list[str] = ["jpg", "jpeg", "png", "pdf"]
    DEBUG: bool = False

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    def split_extensions(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v

    class Config:
        env_file = ".env"


settings = Settings()
