from pydantic import BaseModel, EmailStr    
from datetime import datetime
from typing import Optional
from models import User

class UserBase(BaseModel):
    email: EmailStr
    fullname: str
    password: str
    created_at: datetime
    #age:  Optional[str] = None
    #gender:  Optional[str] = ""

class CreateUser(BaseModel):
    email: EmailStr
    fullname: str
    password: str

class UpdateUser(BaseModel): #email no se puede actualizar, por eso no lo agrego
    fullname: str
    password: str

class UserWithPasswordResponse(UserBase): #Hereda de userBase, toma sus atributos y agrega created_at
    password: str

    class Config:
        orm_mode = True #Para que ignore el orm model, y lo tome como dict para pydantic

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    fullname: str
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token:str
    token_type: str

class TokenData(BaseModel):
    id: int

