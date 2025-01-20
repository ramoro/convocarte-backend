import models
from sqlalchemy.orm import Session

class AcademicExperienceRepository:

    def __init__(self, db: Session):
        self.db = db
    
    def add_new_academic_experience(self, dict_academic_exp):
        new_academic_exp = models.AcademicExperience(
            **dict_academic_exp) #Pasamos el modelo de pydantic a diccionario y luego lo desempaquetamos
        self.db.add(new_academic_exp)
        self.db.commit()
        self.db.refresh(new_academic_exp) #devuelve lo que se guardo recien y se almacena en new_academic_exp

        return new_academic_exp
    
    def get_academic_experiences_by_user_id(self, user_id):
        return self.db.query(models.AcademicExperience).\
                filter((models.AcademicExperience.user_id == user_id)).all()
    
    def get_academic_experience_by_id(self, id):
        return self.db.query(models.AcademicExperience).\
                filter(models.AcademicExperience.id == id).first()
    
    def delete_academic_experience(self, academic_exp_id: int):
        academic_exp = self.db.query(models.AcademicExperience).\
                        filter(models.AcademicExperience.id == academic_exp_id).first()
        if academic_exp:
            self.db.delete(academic_exp)
            self.db.commit()
            return True
        return False
    
    def update_academic_experience(self, academic_exp_id, updated_academic_exp):
        academic_exp_query = self.db.query(models.AcademicExperience).\
                            filter(models.AcademicExperience.id == academic_exp_id)

        if not academic_exp_query.first():
            return None

        academic_exp_query.update(updated_academic_exp, synchronize_session=False)
        self.db.commit()
    
        # Retornar el registro actualizado
        return academic_exp_query.first()


