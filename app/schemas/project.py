from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateProject(BaseModel):
    name: str
    description: Optional[str] = None
    region: str
    category: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    category: str
    created_at: datetime

