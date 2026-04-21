from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    provider: str = "ollama"
    model: str = "llama3.1"
    ollama_base_url: str | None = None
    openrouter_api_key: str | None = None
    anthropic_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()