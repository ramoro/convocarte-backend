from fastapi import HTTPException, Depends, APIRouter
from database import get_db
from starlette import status
from sqlalchemy.orm import Session
import oauth2
import models
from schemas.form_template import CreateFormTemplate
from repository.form_template import FormTemplateRepository

router = APIRouter(
    prefix="/form-templates", 
    tags=["FormTemplates"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_form_template(form_template: CreateFormTemplate, 
                current_user: models.User = Depends(oauth2.get_current_user), 
                db: Session = Depends(get_db)):
    
    form_template_repository = FormTemplateRepository(db)

    if form_template_repository.get_form_template_by_user_id_and_title(current_user.id, form_template.form_template_title):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The user already has a form template with that title")

    if not form_template_repository.add_new_form_template(current_user.id, form_template.form_template_title, form_template.form_template_fields):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the form template")
    
    return {'success': True, 'status_code': status.HTTP_201_CREATED,
            'form_template_title': form_template.form_template_title }


