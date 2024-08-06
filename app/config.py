from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str = "80"
    database_name: str = "convocarte"
    database_username: str
    database_password: str
    
    class Config:
        env_file = "../.env"

settings = Settings()