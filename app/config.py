from pydantic_settings import BaseSettings
import json

class Settings(BaseSettings):
    database_hostname: str
    database_port: str = "80"
    database_name: str = "convocarte"
    database_username: str
    database_password: str
    secret_key: str = "1232"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 180
    smtp_server: str
    smtp_server_port: str
    smtp_server_username: str 
    smtp_server_password: str
    noreply_email: str = "convocartenoreply@gmail.com"
    profile_pictures_path: str = "./static/profile_pictures/"
    cvs_path: str = "./static/curriculums/"
    gallery_shots_path: str = "./static/gallery_shots/"
    backend_url: str
    frontend_url: str = "http://localhost:8080"
    google_credentials: str = ""

    @property
    def google_credentials_dict(self):
        return json.loads(self.google_credentials)

    
    class Config:
        env_file = "../.env"

settings = Settings()