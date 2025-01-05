from typing import List
from fastapi import HTTPException, Depends, APIRouter, Response
from database import get_db
from starlette import status
from sqlalchemy.orm import Session
import oauth2
import models
from schemas.form import FormWithFields
from repository.form import FormRepository

router = APIRouter(
    prefix="/forms", 
    tags=["Forms"]
)


@router.get("/{form_id}", response_model=FormWithFields)
def get_form(form_id: int, current_user: models.User = Depends(oauth2.get_current_user), 
                         db: Session = Depends(get_db)):
    
    form_repository = FormRepository(db)

    form = form_repository.get_form_by_id(form_id)

    if not form:
        raise HTTPException(status_code=404, detail=f"Form with id {form_id} not found.")

    return form

@router.put("/", status_code=status.HTTP_204_NO_CONTENT)
def update_form(form: FormWithFields, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    
    form_repository = FormRepository(db)

    updated_form, error = form_repository.update_form(form)

    if not updated_form:
        if error == "Not Found Error":
            raise HTTPException(status_code=404, detail=f"Form with id {form.id} not found.")
        else:
            raise HTTPException(status_code=500, detail=f"Internal Server Error")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

