from pydantic import BaseModel, model_validator, field_validator
from datetime import date
from typing import Optional, Union
from models import AcademicExperience
from dateutil import parser

class AcademicExperienceBase(BaseModel):
    institution: str
    field_of_study: str
    start_date: date
    end_date: Optional[Union[date, str]] #Puede ser una fecha o cadena vacia ya que no termino el estudio aun
    description: str

    @field_validator('start_date', mode='before')
    def parse_start_date(cls, v):
        if isinstance(v, str):
            try:
                return parser.parse(v).date()
            except ValueError:
                raise ValueError(f'Invalid date format for start_date: {v}')
        return v

    @field_validator('end_date', mode='before')
    def parse_end_date(cls, v):
        if isinstance(v, str):
            if v == "":
                return None
            try:
                return parser.parse(v).date()
            except ValueError:
                raise ValueError(f'Invalid date format for end_date: {v}')
        return v

    @model_validator(mode='after')
    def check_dates(self):
        if self.end_date == None:
            return self 
        if isinstance(self.end_date, date) and self.start_date and self.end_date <= self.start_date:
            raise ValueError('End date must be after start date')
        return self
    
class AcademicExperienceResponse(AcademicExperienceBase):
    id: int
    user_id: int