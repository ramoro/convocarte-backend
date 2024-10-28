from pydantic import BaseModel
from typing import List   

class FormTemplateField(BaseModel):
    title: str
    type: str
    order: int
    is_required: bool

class CreateFormTemplate(BaseModel):
    form_template_title: str
    form_template_fields: List[FormTemplateField]