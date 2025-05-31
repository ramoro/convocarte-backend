from datetime import datetime, date
from pydantic import BaseModel, field_validator, model_validator
from typing import List
from typing import Optional
import pytz
from dateutil import parser
from schemas.project import ProjectResponse

class CastingCallPostulation(BaseModel):
    id: int
    owner_id: int
    state: str
    created_at: datetime
    postulation_data: str
    exposed_role_id: int
    has_unread_messages: Optional[bool] = None
    unread_messages_count: Optional[int] = None

class CastingCallExposedRoleInfo(BaseModel):
    role_id: int
    min_age_required: Optional[int] = None
    max_age_required: Optional[int] = None
    min_height_required: Optional[float] = None
    max_height_required: Optional[float] = None
    hair_colors_required: Optional[str] = None
    additional_requirements: Optional[str] = None
    has_limited_spots: bool
    spots_amount: Optional[int] = None
    occupied_spots: Optional[int] = None
    disabled: bool
    casting_postulations: Optional[List[CastingCallPostulation]] = None

#class CastingCallRoleCreation(CastingCallRole):
#    form_template_id: int #Para la creacion se usa form_template_id, luego al crearse el casting ya se crea un form para el rol dentro del casting

class CastingCallRoleEdition(BaseModel):
    form_id: int

class CreateCastingCall(BaseModel):
    title: str
    project_id: int
    #publication_date: Optional[Union[date, str]] Cuando el casting se crea, se crea en borrador, luego se publica, por eso primero no vienen las fechas
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
    description: Optional[str] = None
    created_at: datetime
    publication_date: Optional[date]
    project: Optional[ProjectResponse] = None
    owner_id: int

class PublishedCastingCallResponse(BaseModel):
    title: str
    state: str
    publication_date: date
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

class CastingCallChangeState(BaseModel):
    title: str
    state: str
    
class CastingCallProject(BaseModel):
    id: int
    name: str
    category: str
    region: str

class ExposedRoleForm(BaseModel):
    id: int
    form_title: str

class ExposedRoleRoleData(BaseModel):
    id: int
    name: str

class CastingCallExposedRole(CastingCallExposedRoleInfo):
    id: int
    form: ExposedRoleForm
    role: ExposedRoleRoleData

class CastingCallResponse(CastingCallPreviewResponse):
    description: Optional[str] = None
    state: str
    expiration_date: Optional[date] = None
    project: CastingCallProject
    exposed_roles: List[CastingCallExposedRole]

class CastingCallFilter(BaseModel):
    date_order: str
    remuneration_types: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    age: Optional[int] = None
    height: Optional[float] = None
    hair_colors: Optional[List[str]] = None