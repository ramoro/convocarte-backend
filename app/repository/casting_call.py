import models
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

class CastingCallRepository:

    def __init__(self, db: Session):
        self.db = db

    def add_new_casting_call(self, casting_call, casting_roles):
        try:
            new_casting_call = models.CastingCall(**casting_call) 

            self.db.add(new_casting_call)
            self.db.flush() #Asi ya la variable se actualiza con el id generado para el casting

            for role in casting_roles:
                role['casting_call_id'] = new_casting_call.id

                new_role = models.RoleByCastingCall(**role)
                self.db.add(new_role)

            self.db.commit()
            self.db.refresh(new_casting_call) 
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None
        
        return new_casting_call
    
    def get_casting_calls_by_user_id(self, user_id):
        return self.db.query(models.CastingCall).filter((models.CastingCall.owner_id == user_id)).all()
    
    def update_casting_call(self, casting_call_id, updated_casting_call):
        casting_call_query = self.db.query(models.CastingCall).filter(models.CastingCall.id == casting_call_id)

        if not casting_call_query.first():
            return None

        casting_call_query.update(updated_casting_call, synchronize_session=False)
        self.db.commit()
    
        # Retornar el registro actualizado
        return casting_call_query.first()
    
    def get_casting_call_by_title_and_state(self, casting_call_title, state):
        
        return self.db.query(models.CastingCall).filter(and_(
            models.CastingCall.title == casting_call_title,
            models.CastingCall.state == state
        )).first()
        

