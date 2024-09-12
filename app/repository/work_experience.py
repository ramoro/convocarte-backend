import models
from database import get_db
from sqlalchemy.orm import Session

class WorkExperienceRepository:

    def __init__(self):
        self.db: Session = next(get_db()) 
    
    def add_new_work_experience(self, dict_work_exp):
        new_work_exp = models.WorkExperience(
            **dict_work_exp) #Pasamos el modelo de pydantic a diccionario y luego lo desempaquetamos
        self.db.add(new_work_exp)
        self.db.commit()
        self.db.refresh(new_work_exp) #devuelve lo que se guardo recien y se almacena en new_work_exp

        return new_work_exp
    
    def get_work_experiences_by_user_id(self, user_id):
        return self.db.query(models.WorkExperience).filter((models.WorkExperience.user_id == user_id)).all()
    
    def get_work_experience_by_id(self, id):
        return self.db.query(models.WorkExperience).filter(models.WorkExperience.id == id).first()
    
    def delete_work_experience(self, work_exp_id: int):
        work_exp = self.db.query(models.WorkExperience).filter(models.WorkExperience.id == work_exp_id).first()
        if work_exp:
            self.db.delete(work_exp)
            self.db.commit()
            return True
        return False
    
    def update_work_experience(self, work_exp_id, updated_work_exp):
        work_exp_query = self.db.query(models.WorkExperience).filter(models.WorkExperience.id == work_exp_id)

        if not work_exp_query.first():
            return None

        work_exp_query.update(updated_work_exp, synchronize_session=False)
        self.db.commit()
    
        # Retornar el registro actualizado
        return work_exp_query.first()


