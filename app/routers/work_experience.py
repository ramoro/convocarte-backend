from fastapi import HTTPException, Depends, APIRouter, Response
from database import get_db
from starlette import status
from sqlalchemy.orm import Session
import oauth2
import models
from schemas.work_experience import WorkExperienceBase, WorkExperienceResponse, WorkExperienceUpdate
from repository.work_experience import WorkExperienceRepository
from typing import List

router = APIRouter(
    prefix="/work-experiences", 
    tags=["WorkExperiences"]
)

@router.post("/", response_model=WorkExperienceResponse)
async def add_work_experience(new_work_experience: WorkExperienceBase, 
                                  current_user: models.User = Depends(oauth2.get_current_user),
                                  db: Session = Depends(get_db)):
    work_exp_repository = WorkExperienceRepository(db)
    dict_work_exp = new_work_experience.model_dump()
    dict_work_exp['user_id'] = current_user.id
    new_work_exp = work_exp_repository.add_new_work_experience(dict_work_exp)

    return new_work_exp

@router.get("/", response_model=List[WorkExperienceResponse])
async def list_work_experiences(current_user: models.User = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    work_exp_repository = WorkExperienceRepository(db)
    
    my_work_experiences = work_exp_repository.get_work_experiences_by_user_id(current_user.id)

    return my_work_experiences

@router.delete("/{work_exp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_experience(work_exp_id: int, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    work_exp_repository = WorkExperienceRepository(db)

    deleted = work_exp_repository.delete_work_experience(work_exp_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Work experience {work_exp_id} not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{work_exp_id}", response_model=WorkExperienceBase)
def update_work_experience(work_exp_id: int, updated_work_exp: WorkExperienceUpdate, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    work_exp_repository = WorkExperienceRepository(db)
    updated_exp = work_exp_repository.update_work_experience(work_exp_id, updated_work_exp.model_dump())

    if not updated_exp:
        raise HTTPException(status_code=404, detail=f"Work experience {work_exp_id} not found")

    return updated_exp
