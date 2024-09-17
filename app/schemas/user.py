from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

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
    password_confirmation: str

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

class UserFullResponse(UserResponse):
    weight: Optional[float]
    height: Optional[float]
    eyes_color: Optional[str]
    skin_color: Optional[str]
    waist_measurement: Optional[float]
    hip_measurement: Optional[float]
    bust_measurement: Optional[float]
    hair_color: Optional[str]
    pant_size: Optional[float]
    tshirt_size: Optional[float]
    jacket_size: Optional[float]
    shoes_size: Optional[float]
    hands: Optional[str]
    feet: Optional[str]
    teeth: Optional[str]
    braces: Optional[bool]
    tattoos: Optional[bool]
    tattoosArea: Optional[str]
    piercings: Optional[bool]
    piercingsArea: Optional[str]
    physical_characs_extra_info: Optional[str]

class UpdateUser(BaseModel):
    weight: Optional[float]
    height: Optional[float]
    eyes_color: Optional[str]
    skin_color: Optional[str]
    waist_measurement: Optional[float]
    hip_measurement: Optional[float]
    bust_measurement: Optional[float]
    hair_color: Optional[str]
    pant_size: Optional[float]
    tshirt_size: Optional[float]
    jacket_size: Optional[float]
    shoes_size: Optional[float]
    hands: Optional[str]
    feet: Optional[str]
    teeth: Optional[str]
    braces: Optional[bool]
    tattoos: Optional[bool]
    tattoosArea: Optional[str]
    piercings: Optional[bool]
    piercingsArea: Optional[str]
    physical_characs_extra_info: Optional[str]

class Token(BaseModel):
    access_token:str
    token_type: str

class TokenData(BaseModel):
    id: int

class ForgetPasswordRequest(BaseModel):
    email: str

class ResetForgetPassword(BaseModel):
    secret_token: str
    new_password: str
    password_confirmation: str