from pydantic import BaseModel, EmailStr    

class UserLogin(BaseModel):
    email: str
    password: str