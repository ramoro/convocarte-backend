from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, date
from typing import Optional, Union
from dateutil import parser

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
    cv: Optional[str]
    reel_link: Optional[str]
    profile_picture: Optional[str]

    chest_up_shot: Optional[str]
    full_body_shot: Optional[str]
    profile_shot: Optional[str]
    additional_shot_1: Optional[str]
    additional_shot_2: Optional[str]

    age: Optional[int]
    gender: Optional[str]
    residence_country: Optional[str]
    locality: Optional[str]
    nationality: Optional[str]
    birth_date:Optional[Union[date, str]]
    phone_number: Optional[str]
    phone_number_two: Optional[str]
    instagram: Optional[str]
    facebook: Optional[str]
    youtube_channel: Optional[str]
    website: Optional[str]

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

    language_skills: Optional[str]
    sports_skills: Optional[str]
    instruments_skills: Optional[str]
    other_skills: Optional[str]
    is_singer: Optional[bool]
    is_dancer: Optional[bool]
    dance_types: Optional[str]
    car_drivers_license: Optional[bool]
    moto_drivers_license: Optional[bool]
    skills_additionals: Optional[str]

class UpdateUser(BaseModel):
    cv: Optional[str] = None
    reel_link: Optional[str] = None

    chest_up_shot: Optional[str] = None
    full_body_shot: Optional[str] = None
    profile_shot: Optional[str] = None
    additional_shot_1: Optional[str] = None
    additional_shot_2: Optional[str] = None

    fullname: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    residence_country: Optional[str] = None
    locality: Optional[str] = None
    nationality: Optional[str] = None
    birth_date:Optional[Union[date, str]] = None
    phone_number: Optional[str] = None
    phone_number_two: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    youtube_channel: Optional[str] = None
    website: Optional[str] = None

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

    language_skills: Optional[str] = None
    sports_skills: Optional[str] = None
    instruments_skills: Optional[str] = None
    other_skills: Optional[str] = None
    is_singer: Optional[bool] = None
    is_dancer: Optional[bool] = None
    dance_types: Optional[str] = None
    car_drivers_license: Optional[bool] = None
    moto_drivers_license: Optional[bool] = None
    skills_additionals: Optional[str] = None

    @field_validator('birth_date', mode='before')
    def parse_publication_date(cls, v):
        if isinstance(v, str):
            try:
                return parser.parse(v).date()
            except ValueError:
                raise ValueError(f'Invalid date format for publication_date: {v}')
        return v


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

class DeleteUserFile(BaseModel):
    field_name: str
    file_name: str