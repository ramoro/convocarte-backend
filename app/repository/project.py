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
    
    def add_new_project(self, dict_project):

        try:
            new_project = models.Project(**dict_project) 

            self.db.add(new_project)

            self.db.commit()
            self.db.refresh(new_project) 
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None
        
        return new_project
    
    def get_projects_by_user_id(self, user_id):
        return self.db.query(models.Project).filter((models.Project.owner_id == user_id)).all()

