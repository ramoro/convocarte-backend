from typing import List
from fastapi import HTTPException, Depends, APIRouter, Response
from database import get_db
from starlette import status
from sqlalchemy.orm import Session
import oauth2
import models
from schemas.project import CreateProject, ProjectResponse, ProjectWithRolesResponse
from repository.project import ProjectRepository

router = APIRouter(
    prefix="/projects", 
    tags=["Projects"]
)

def project_has_roles_with_same_name(roles):
    """Recibe una lista de Roles.
    Devuelve true si se repiten roles con mismo nombre, False en caso contrario."""
    role_names = {}

    for role in roles:
        if role.name not in role_names:
            role_names[role.name] = 1
        else:
            return True
        
    return False

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_form_template(new_project: CreateProject, 
                current_user: models.User = Depends(oauth2.get_current_user), 
                db: Session = Depends(get_db)):
    
    project_repository = ProjectRepository(db)
    dict_project = new_project.model_dump()
    dict_project['owner_id'] = current_user.id
    roles = new_project.roles
    dict_project.pop('roles')

    if project_repository.get_project_by_user_id_and_title(current_user.id, new_project.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The user already has a project with the name "+ new_project.name)

    if project_has_roles_with_same_name(roles):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The project has two roles with the same name")

    if not project_repository.add_new_project(dict_project, roles):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the project")
    
    return {'success': True, 'status_code': status.HTTP_201_CREATED,
            'project_name': new_project.name  }

@router.get("/", response_model=List[ProjectResponse])
def get_user_projects(current_user: models.User = Depends(oauth2.get_current_user), 
                         db: Session = Depends(get_db)):
    
    project_repository = ProjectRepository(db)

    my_projects = project_repository.get_projects_by_user_id(current_user.id)

    return my_projects

@router.get("/with-roles", response_model=List[ProjectWithRolesResponse])
def get_user_projects_with_roles(current_user: models.User = Depends(oauth2.get_current_user), 
                         db: Session = Depends(get_db)):
    
    project_repository = ProjectRepository(db)

    my_projects_with_roles = project_repository.get_user_projects_with_roles(current_user.id)

    return my_projects_with_roles