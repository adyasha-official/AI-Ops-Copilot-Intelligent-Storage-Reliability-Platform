from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./ops.db"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"
    cors_origins: str = "http://localhost:5173"
    auto_seed: bool = True  # seed 100 simulated drives if the DB is empty


settings = Settings()
