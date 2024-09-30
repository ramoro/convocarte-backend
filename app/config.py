from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str = "80"
    database_name: str = "convocarte"
    database_username: str
    database_password: str
    secret_key: str = "1232"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    smtp_server: str
    smtp_server_port: str
    smtp_server_username: str
    smtp_server_password: str
    noreply_email: str
    profile_pictures_path: str
    cvs_path: str
    
    class Config:
        env_file = "../.env"

settings = Settings()