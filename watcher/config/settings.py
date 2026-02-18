from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POLL_INTERVAL_SECONDS: int = 900  # 15 minutes
    PAGE_SIZE: int = 500

    # Bootstrap control
    BOOTSTRAP_DAYS: int = 1

    class Config:
        env_file = ".env"


settings = Settings()