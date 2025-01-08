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
def create_project(new_project: CreateProject, 
                current_user: models.User = Depends(oauth2.get_current_user), 
                db: Session = Depends(get_db)):
    
    project_repository = ProjectRepository(db)
    dict_project = new_project.model_dump()
    dict_project['owner_id'] = current_user.id
    dict_project['is_used'] = False
    roles = new_project.roles
    dict_project.pop('roles')

    if not roles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The project must have at least one role")

    if project_repository.get_project_by_user_id_and_title(current_user.id, new_project.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The user already has a project with the name "+ new_project.name)

    if project_has_roles_with_same_name(roles):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The project mustnt have two roles with the same name")

    new_project = project_repository.add_new_project(dict_project, roles)

    if not new_project:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the project")
    
    return {'success': True, 'status_code': status.HTTP_201_CREATED,
            'project_name': new_project.name, 'id': new_project.id  }

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

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    
    project_repository = ProjectRepository(db)

    project = project_repository.get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found.")

    #Si el proyecto esta siendo en algun casting no finalizado no puede eliminarse
    if project.is_used:
        raise HTTPException(status_code=400, detail="The project cant be deleted cause its being used by a casting call.")

    deleted_project = project_repository.delete_project(project_id)
    
    if not deleted_project:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An error occurred while deleting the project")  

    return Response(status_code=status.HTTP_204_NO_CONTENT)
