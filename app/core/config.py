from pydantic_settings import BaseSettings
from pydantic import Field
class Settings(BaseSettings):
    app_name: str = Field(default="Medical AI TechRadar", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    request_timeout_s: int = Field(default=15, alias="REQUEST_TIMEOUT_S")
    retry_max: int = Field(default=2, alias="RETRY_MAX")
    model_config = {"env_file": ".env", "extra": "ignore"}
    max_concurrency: int = Field(default=5, alias="MAX_CONCURRENCY")
    request_timeout_s: int = Field(default=10, alias="REQUEST_TIMEOUT_S")
    retry_max: int = Field(default=3, alias="RETRY_MAX")
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
settings = Settings()