from pydantic import BaseSettings

class Settings(BaseSettings):
    fingerprint_reader_port: str = "/dev/ttyUSB0"
    database_url: str = "sqlite:///./test.db"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()