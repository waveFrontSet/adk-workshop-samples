from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ai_model: str = "gemini-2.5-flash"


settings = Settings()
