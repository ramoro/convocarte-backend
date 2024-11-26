from datetime import date
from pydantic import BaseModel
from typing import List
from typing import Optional, Union

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
    title: str
    remuneration_type: str
    state: str
    casting_photos: Optional[str] = None #Se manda solo una, la primera, que funciona como portada
