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
    
    def get_casting_postulation_by_user_and_open_role(self, user_id, open_role_id):
        """Recibe el id de un usuario y el id de un rol expuesto. Devuelve la postulacion del usuario
        a ese rol expuesto en caso de existir, sino devuelve None."""
        return self.db.query(models.CastingPostulation).filter(
            and_(
                models.CastingPostulation.owner_id == user_id,
                models.CastingPostulation.open_role_id == open_role_id
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
                joinedload(models.CastingPostulation.open_role)
                .joinedload(models.OpenRole.role)
            )
            .first()
        )
    
        return casting_postulation
    
    def get_casting_postulations_by_user(self, user_id):
        """Recibe el id de un usuario y devuelve todas las postulaciones que ha hecho
        con datos del casting y del proyecto, incluyendo conteo de mensajes no leídos."""
        postulations = (
            self.db.query(models.CastingPostulation)
            .filter(
                models.CastingPostulation.owner_id == user_id,
                models.CastingPostulation.deleted_at == None
            )
            .options(
                joinedload(models.CastingPostulation.open_role)
                .joinedload(models.OpenRole.casting_call)
                .joinedload(models.CastingCall.project),
                joinedload(models.CastingPostulation.messages)  # Cargar todos los mensajes
            )
            .order_by(models.CastingPostulation.created_at.desc())
            .all()
        )

        # Procesar cada postulación para agregar la info necesaria
        result = []
        for postulation in postulations:
            # Contar mensajes no leídos donde el receptor es el usuario
            unread_count = sum(
                1 for message in postulation.messages
                if "Sin Leer" in message.state  and message.sender_id != user_id
            )

            result.append({
                "id": postulation.id,
                "state": postulation.state,
                "created_at": postulation.created_at,
                "remuneration_type": postulation.open_role.casting_call.remuneration_type,
                "project_name": postulation.open_role.casting_call.project.name,
                "category": postulation.open_role.casting_call.project.category,
                "region": postulation.open_role.casting_call.project.region,
                "unread_messages_count": unread_count,
                "has_unread_messages": unread_count > 0
            })

        return result

    
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
        
    def choose_casting_postulation(self, postulation_id):
        casting_postulation_query = self.db.query(models.CastingPostulation).\
                            filter(models.CastingPostulation.id == postulation_id)
        
        casting_postulation = casting_postulation_query.first()

        if not casting_postulation:
            return None

        casting_postulation_query.update({'state': 'Elegida'}, synchronize_session=False)
        casting_postulation.open_role.role.assigned_user_id = casting_postulation.owner_id
        self.db.commit()
    
        # Retorna el registro actualizado
        return casting_postulation
    
    def remove_chosen_casting_postulation(self, postulation_id):
        casting_postulation_query = self.db.query(models.CastingPostulation).\
                            filter(models.CastingPostulation.id == postulation_id)
        
        casting_postulation = casting_postulation_query.first()

        if not casting_postulation:
            return None

        casting_postulation_query.update({'state': 'Pendiente'}, synchronize_session=False)
        casting_postulation.open_role.role.assigned_user_id = None
        self.db.commit()
    
        # Retorna el registro actualizado
        return casting_postulation