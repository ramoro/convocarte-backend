from datetime import datetime
from pydantic import BaseModel
from typing import List
from typing import Optional

class FormField(BaseModel):
    title: str
    type: str
    order: int
    is_required: bool

class FormWithFields(BaseModel):
    id: int
    form_title: str
    created_at: Optional[datetime] = None
    form_fields: List[FormField]
