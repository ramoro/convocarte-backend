from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Role(BaseModel):
    name: str
    description: Optional[str] = None

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

class ProjectWithRolesResponse(ProjectResponse):
    roles: List[RoleWithId]

class UpdateProject(BaseModel):
    name: str
    category: str
    is_used: bool
    description: Optional[str] = None
    region: str
    roles: List[Role]
