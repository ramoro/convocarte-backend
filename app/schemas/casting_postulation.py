from typing import List, Optional
from pydantic import BaseModel
from schemas.casting_call import CastingCallPreviewResponse
from datetime import datetime
class Role(BaseModel):
    id: int
    name: str
    description: str

class OpenRole(BaseModel):
    id: int
    role: Role

class CastingPostulationResponse(BaseModel):
    id: int
    state: str
    postulation_data: str
    casting_call: CastingCallPreviewResponse
    open_role: OpenRole
    created_at: datetime
    owner_id: int

class CastingPostulationPreview(BaseModel):
    id: int
    state: str
    created_at: datetime

class CastingPostulationPreviewExtraData(CastingPostulationPreview):
    remuneration_type: str
    project_name: str
    category: str
    region: str
    has_unread_messages: Optional[bool] = None
    unread_messages_count: Optional[int] = None

class CastingPostulationUpdate(BaseModel):
    state: str
    postulation_data: str

class CastingPostulationIds(BaseModel):
    ids: List[int]