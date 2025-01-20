from typing import List
from fastapi import HTTPException, Depends, APIRouter, Response
from database import get_db
from starlette import status
from sqlalchemy.orm import Session
import oauth2
import models
from schemas.form import FormWithFields
from repository.form import FormRepository
from repository.casting_call import CastingCallRepository

router = APIRouter(
    prefix="/forms", 
    tags=["Forms"],
    dependencies=[Depends(oauth2.get_current_user)]
)


@router.get("/{form_id}", response_model=FormWithFields)
def get_form(form_id: int,
            db: Session = Depends(get_db)):
    
    form_repository = FormRepository(db)

    form = form_repository.get_form_by_id(form_id)

    if not form:
        raise HTTPException(status_code=404, detail=f"Form with id {form_id} not found.")

    return form

@router.put("/", status_code=status.HTTP_204_NO_CONTENT)
def update_form(updated_form: FormWithFields, db: Session = Depends(get_db)):
    
    form_repository = FormRepository(db)
    casting_call_repository = CastingCallRepository(db)

    form = form_repository.get_form_by_id(updated_form.id)

    if not form:
        raise HTTPException(status_code=404, detail=f"Form with id {updated_form.id} not found.")
    
    #Valida que el form no pertenezca a un casting publicado o finalizado
    casting_call = casting_call_repository.get_casting_call_by_id(form.casting_call_id)
    casting_state = casting_call.state

    if casting_state == "Publicado":
        raise HTTPException(status_code=400, 
                            detail="The form cant be updated cause its casting call is published. Pause it to update the form.")
    if casting_state == "Finalizado":
        raise HTTPException(status_code=400, 
                            detail="The form cant be updated cause its casting call has finished.")

    result = form_repository.update_form(form, updated_form)

    if not result:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

