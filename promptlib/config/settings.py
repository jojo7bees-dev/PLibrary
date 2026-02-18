import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    storage_backend: str = "sqlite" # sqlite, json, yaml
    sqlite_url: str = "sqlite:///promptlib.db"
    json_dir: str = "prompts_json"
    yaml_dir: str = "prompts_yaml"
    log_level: str = "INFO"

    class Config:
        env_prefix = "PROMPTLIB_"

settings = Settings()
