from datetime import datetime, date
from pydantic import BaseModel, field_validator, model_validator
from typing import List
from typing import Optional
import pytz
from dateutil import parser


class CastingCallRole(BaseModel):
    role_id: int
    form_template_id: int
    min_age_required: Optional[int] = None
    max_age_required: Optional[int] = None
    min_height_required: Optional[int] = None
    max_height_required: Optional[int] = None
    hair_colors_required: Optional[str] = None
    additional_requirements: Optional[str] = None
    has_limited_spots: bool
    spots_amount: Optional[int] = None

class CreateCastingCall(BaseModel):
    title: str
    project_id: int
    #start_date: Optional[Union[date, str]] Cuando el casting se crea, se crea en borrador, luego se publica, por eso primero no vienen las fechas
    #expiration_date: Optional[Union[date, str]]
    remuneration_type: str
    description: Optional[str] = None
    #casting_photos se tratan a parte, se reciben como UploadFile
    state: Optional[str] = None
    #roles: List[CastingCallRole]

class CastingCallPreviewResponse(BaseModel):
    id: int
    title: str
    remuneration_type: str
    state: str
    casting_photos: Optional[List[str]] = None
    created_at: datetime

class PublishedCastingCallResponse(BaseModel):
    title: str
    state: str
    start_date: date
    expiration_date: date

class CastingCallPublication(BaseModel):
    title: str
    state: str
    expiration_date: date

    @field_validator('expiration_date', mode='before')
    def parse_end_date(cls, v):
        if isinstance(v, str):
            if v == "":
                return None
            try:
                return parser.parse(v).date()
            except ValueError:
                raise ValueError(f'Invalid date format for expiration_date: {v}')
        return v

    @model_validator(mode='after')
    def check_dates(self):
        if self.expiration_date is None:
            return self

        # Zona horaria de Argentina
        argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
        today = datetime.now(argentina_tz).date()

        if self.expiration_date <= today:
            raise ValueError(f'Expiration date must be after the current date: {today}')
        
        return self
