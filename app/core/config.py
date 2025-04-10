from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Warehouse Monitoring"
    SQLALCHEMY_DATABASE_URL: str
    KAFKA_BROKER: str

    class Config:
        env_file = ".env.example"


settings = Settings()
