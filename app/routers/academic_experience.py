from fastapi import HTTPException, Depends, APIRouter, Response
from database import get_db
from starlette import status
from sqlalchemy.orm import Session
import oauth2
import models
from schemas.academic_experience import AcademicExperienceBase, AcademicExperienceUpdate, AcademicExperienceResponse
from repository.academic_experience import AcademicExperienceRepository
from typing import List

router = APIRouter(
    prefix="/academic-experiences", 
    tags=["AcademicExperiences"]
)

@router.post("/", response_model=AcademicExperienceResponse)
async def add_academic_experience(new_academic_experience: AcademicExperienceBase, 
                                  current_user: models.User = Depends(oauth2.get_current_user),
                                  db: Session = Depends(get_db)):
    academic_exp_repository = AcademicExperienceRepository(db)
    dict_academic_exp = new_academic_experience.model_dump()
    dict_academic_exp['user_id'] = current_user.id
    new_academic_exp = academic_exp_repository.add_new_academic_experience(dict_academic_exp)

    return new_academic_exp

@router.get("/", response_model=List[AcademicExperienceResponse])
async def list_academic_experiences(current_user: models.User = Depends(oauth2.get_current_user),
                                    db: Session = Depends(get_db)):
    academic_exp_repository = AcademicExperienceRepository(db)
    
    my_academic_experiences = academic_exp_repository.get_academic_experiences_by_user_id(current_user.id)

    return my_academic_experiences

@router.delete("/{academic_exp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_academic_experience(academic_exp_id: int, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    academic_exp_repository = AcademicExperienceRepository(db)

    deleted = academic_exp_repository.delete_academic_experience(academic_exp_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Academic experience {academic_exp_id} not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{academic_exp_id}", response_model=AcademicExperienceBase)
def update_academic_experience(academic_exp_id: int, updated_academic_exp: AcademicExperienceUpdate, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    academic_exp_repository = AcademicExperienceRepository(db)
    updated_exp = academic_exp_repository.update_academic_experience(academic_exp_id, updated_academic_exp.model_dump())

    if not updated_exp:
        raise HTTPException(status_code=404, detail=f"Academic experience {academic_exp_id} not found")

    return updated_exp
