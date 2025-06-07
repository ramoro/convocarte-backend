import models
from sqlalchemy.orm import Session

class OpenRoleRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_open_role_with_casting_by_form_id(self, form_id):
        """Recibe el id de un form. Obtiene la información del rol expuesto que tiene asociado y el casting
        al que pertenece ese rol. Devuelve un diccionario con la información obtenida usando como clave los nombres
        de los campos que corresponden para cada dato."""
        result =  self.db.query(models.OpenRole.has_limited_spots, models.OpenRole.spots_amount, 
                models.OpenRole.occupied_spots, models.CastingCall.title, 
                models.CastingCall.publication_date, models.CastingCall.state, models.CastingCall.id, 
                models.OpenRole.id).\
                join(models.CastingCall, models.OpenRole.casting_call_id == models.CastingCall.id).\
                filter(models.OpenRole.form_id == form_id).first()

        if result:
            data_with_columns = {
                'has_limited_spots': result[0],
                'spots_amount': result[1],
                'occupied_spots': result[2],
                'casting_call_title': result[3],
                'casting_call_publication_date': result[4],
                'casting_call_state': result[5],
                'casting_call_id': result[6],
                'open_role_id': result[7]
            }

        return data_with_columns
    
    def update_occupied_spots(self, open_role_id, occupied_spots):
        self.db.query(models.OpenRole).filter(models.OpenRole.id == open_role_id).\
        update({'occupied_spots': occupied_spots})
        self.db.commit()
