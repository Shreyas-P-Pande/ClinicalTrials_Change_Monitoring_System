from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "ClinicalTrials Monitor"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "local"

    class Config:
        env_file = ".env"


settings = Settings()