import models
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

class CastingPostulationRepository:

    def __init__(self, db: Session):
        self.db = db

    def add_new_casting_postulation(self, casting_postulation, postulation_data):
        """Recibe un diccionario con la informacion de una postulacion para cierto rol dentro
        de un casting. Crea la postulacion en la BDD y devuelve el objeto creado."""
        new_casting_postulation = models.CastingPostulation(**casting_postulation) 
        new_casting_postulation.set_postulation_data(postulation_data)

        self.db.add(new_casting_postulation)
        self.db.commit()
        self.db.refresh(new_casting_postulation) 

        return new_casting_postulation
    
    def get_casting_postulation_by_user_and_exposed_role(self, user_id, exposed_role_id):
        """Recibe el id de un usuario y el id de un rol expuesto. Devuelve la postulacion del usuario
        a ese rol expuesto en caso de existir, sino devuelve None."""
        return self.db.query(models.CastingPostulation).filter(
            and_(
                models.CastingPostulation.owner_id == user_id,
                models.CastingPostulation.exposed_role_id == exposed_role_id
            )).first()
    
    def get_casting_postulation_by_id(self, casting_postulation_id):
        """Recibe el id de una postulacion y devuelve toda su informacion, junto con la info
        del casting asociado y del rol al que pertenece."""
        casting_postulation = (
            self.db.query(models.CastingPostulation)
            .filter(models.CastingPostulation.id == casting_postulation_id)
            .options(
                joinedload(models.CastingPostulation.casting_call),
                joinedload(models.CastingPostulation.exposed_role)
                .joinedload(models.ExposedRole.role)
            )  
            .first()
        )
    
        return casting_postulation