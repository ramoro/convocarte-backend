import models
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

class ProjectRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_project_by_user_id_and_title(self, user_id, project_name):
        return self.db.query(models.Project).filter(
            and_(
                models.Project.owner_id == user_id,
                models.Project.name == project_name
            )).first()
    
    def add_new_project(self, dict_project, roles):
        """Recibe un diccionario con los datos de un proyecto y una lista de diccionarios, cada uno
        con la información de un rol perteneciente al prouecto. Agrega el proyecto en la tabla Projects
        y cada rol con el proyecto asociado en la tabla Roles. Devuelve el proyecto almacenado o None en caso 
        contrario."""
        try:
            new_project = models.Project(**dict_project) 

            self.db.add(new_project)
            self.db.flush() #Asi ya la variable se actualiza con el id generado para el proyecto

            for role in roles:
                new_role = models.Role(
                    project_id=new_project.id,
                    name=role.name,
                    description=role.description
                )
                self.db.add(new_role)

            self.db.commit()
            self.db.refresh(new_project) 
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None
        
        return new_project
    
    def get_projects_by_user_id(self, user_id):
        return self.db.query(models.Project).filter((models.Project.owner_id == user_id)).all()
    
    def get_user_projects_with_roles(self, user_id):
        projects = self.db.query(models.Project).filter(models.Project.owner_id == user_id).\
        options(joinedload(models.Project.roles)).all()

        return projects
    
    def get_project_by_id(self, project_id):
        return self.db.query(models.Project).filter((models.Project.id == project_id)).first()
    


