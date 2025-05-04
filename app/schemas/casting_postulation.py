from typing import List, Optional
from pydantic import BaseModel
from schemas.casting_call import CastingCallPreviewResponse
from datetime import datetime
class Role(BaseModel):
    id: int
    name: str
    description: str

class ExposedRole(BaseModel):
    id: int
    role: Role

class CastingPostulationResponse(BaseModel):
    id: int
    state: str
    postulation_data: str
    casting_call: CastingCallPreviewResponse
    exposed_role: ExposedRole
    created_at: datetime

class CastingPostulationPreview(BaseModel):
    id: int
    state: str
    created_at: datetime

class CastingPostulationPreviewExtraData(CastingPostulationPreview):
    remuneration_type: str
    project_name: str
    category: str
    region: str

class CastingPostulationUpdate(BaseModel):
    state: str
    postulation_data: str

class CastingPostulationIds(BaseModel):
    ids: List[int]
