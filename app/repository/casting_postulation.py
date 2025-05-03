from datetime import datetime, timezone
import models
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, update

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
                joinedload(models.CastingPostulation.casting_call)
                .joinedload(models.CastingCall.project),
                joinedload(models.CastingPostulation.exposed_role)
                .joinedload(models.ExposedRole.role)
            )
            .first()
        )
    
        return casting_postulation
    
    def get_casting_postulations_by_user(self, user_id):
        """Recibe el id de un usuario y devuelve todas las postulaciones que ha hecho
        con datos del casting y del proyecto."""
        postulations = (
            self.db.query(
                models.CastingPostulation.id,
                models.CastingPostulation.state,
                models.CastingPostulation.created_at,
                # models.CastingCall.title,
                # models.CastingCall.description,
                models.CastingCall.remuneration_type,
                # models.CastingCall.status,
                # models.CastingCall.photos,
                # models.Role.name,
                # models.Role.description,
                models.Project.name.label("project_name"),
                models.Project.category,
                models.Project.region,
            )
            .join(models.CastingPostulation.exposed_role)
            .join(models.ExposedRole.casting_call)
            .join(models.CastingCall.project)
            .filter(and_(models.CastingPostulation.owner_id == user_id,
                         models.CastingPostulation.deleted_at == None))
            .order_by(models.CastingPostulation.created_at.desc())
            .all()
        )

        result = [dict(row._mapping) for row in postulations]
        return result

    def get_casting_postulations_by_casting_call(self, casting_call_id):
        """Recibe el id de un casting y devuelve todas las postulaciones realizadas a ese casting. Salvo
        las que están en estado 'Rechazada'."""
        postulations = (
            self.db.query(models.CastingPostulation)
            .filter(and_(models.CastingPostulation.casting_call_id == casting_call_id,
                        #models.CastingPostulation.deleted_at == None,
                        #DEVUELVE LAS ELIMINADAS, PUES SI EL USUARIO SE POSTULO, EL DIRECTOR DE CASTING
                        #DEBERIA AUN PODER TENER LA POSIBILIDAD DE VER LA POSTULACION
                        models.CastingPostulation.state != "Rechazada")) 
                        #Diferenciar de rechazada por mensaje de las que estan en estado rechazada. 
                        #Si se rechazo por mensaje, el casting sigue mostrando la postulacion,
                        #por si se quiere volver a tener contacto. Rechazada asi solo
                        #significa que se elimino de la lista de postulaciones del casting

            .all()
        )
        return postulations
    
    def update_casting_postulation(self, casting_postulation_id, updated_casting_postulation):
        """Recibe el id de una postulacion y un diccionaro con los datos a actualizar. Devuelve
        None si no existe la postulacion, sino devuelve el objeto actualizado."""
        print(casting_postulation_id)
        casting_postulation_query = self.db.query(models.CastingPostulation).\
                            filter(models.CastingPostulation.id == casting_postulation_id)

        if not casting_postulation_query.first():
            return None

        casting_postulation_query.update(updated_casting_postulation, synchronize_session=False)
        self.db.commit()
    
        # Retorna el registro actualizado
        return casting_postulation_query.first()
    
    def delete_casting_postulation(self, casting_postulation):
        try:
            casting_postulation.deleted_at = datetime.now(timezone.utc)
            casting_postulation.state = "Eliminada"

            self.db.add(casting_postulation)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def update_casting_postulations_state(self, casting_postulation_ids, new_state):
        """Recibe un listado de ids de postulaciones y cambia su estado a new_state."""
        try:
            update_query = update(models.CastingPostulation).where(
                models.CastingPostulation.id.in_(casting_postulation_ids)
            ).values(state=new_state)
            
            self.db.execute(update_query)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
