from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Role(BaseModel):
    name: str
    description: Optional[str] = None
    assigned_user_name: Optional[str] = None

class RoleWithId(Role):
    id: int

class CreateProject(BaseModel):
    name: str
    description: Optional[str] = None
    region: str
    category: str
    roles: List[Role]

class ProjectResponse(BaseModel):
    id: int
    name: str
    category: str
    created_at: datetime
    is_used: bool
    region: str
    description: Optional[str] = None

class CastingCallProjectPreview(BaseModel):
    title: str
    state: str

class ProjectWithRolesAndCastingsResponse(ProjectResponse):
    roles: List[RoleWithId]
    castings: Optional[List[CastingCallProjectPreview]] = None

class UpdateProject(BaseModel):
    name: str
    category: str
    is_used: bool
    description: Optional[str] = None
    region: str
    roles: List[Role]