import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_DB: str
    MONGO_IP: str
    MONGO_PORT: int
    MONGO_USER: str
    MONGO_PWD: str

    class Config:
        env_file = 'app/.env'


settings = Settings()