from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OLLAMA_API_URL: str = ""
    OLLAMA_MODEL: str = ""
    GEMINI_API_KEY: str = ""
    UPLOAD_DIR: str = "./app/uploads"
    MAX_FILE_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: str = "pdf"
    DEBUG: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
