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
    pant_size: Optional[str]
    tshirt_size: Optional[str]
    jacket_size: Optional[str]
    shoes_size: Optional[str]
    hands: Optional[str]
    feet: Optional[str]
    teeth: Optional[str]
    braces: Optional[bool]
    tattoos: Optional[bool]
    tattoos_area: Optional[str]
    piercings: Optional[bool]
    piercings_area: Optional[str]
    physical_characs_extra_info: Optional[str]

class UpdateUser(BaseModel):
    weight: Optional[float] = None
    height: Optional[float] = None
    eyes_color: Optional[str] = None
    skin_color: Optional[str] = None
    waist_measurement: Optional[float] = None
    hip_measurement: Optional[float] = None
    bust_measurement: Optional[float] = None
    hair_color: Optional[str] = None
    pant_size: Optional[str] = None
    tshirt_size: Optional[str] = None
    jacket_size: Optional[str] = None
    shoes_size: Optional[str] = None
    hands: Optional[str] = None
    feet: Optional[str] = None
    teeth: Optional[str] = None
    braces: Optional[bool] = None
    tattoos: Optional[bool] = None
    tattoos_area: Optional[str] = None
    piercings: Optional[bool] = None
    piercings_area: Optional[str] = None 
    physical_characs_extra_info: Optional[str] = None


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