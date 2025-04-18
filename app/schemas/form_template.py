from datetime import datetime
from pydantic import BaseModel
from typing import List
from typing import Optional

class FormTemplateField(BaseModel):
    title: str
    type: str
    order: int
    is_required: bool

class CreateFormTemplate(BaseModel):
    form_template_title: str
    form_template_fields: List[FormTemplateField]

class FormTemplateResponse(BaseModel):
    id: int
    form_template_title: str
    created_at: datetime

class FormTemplateWithFields(BaseModel):
    id: int
    form_template_title: str
    created_at: Optional[datetime] = None
    form_template_fields: List[FormTemplateField]
    
class UpdateFormTemplate(FormTemplateWithFields):
    original_form_template_title: str
