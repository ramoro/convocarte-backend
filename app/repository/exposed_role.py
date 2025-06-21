import models
from sqlalchemy.orm import Session

class ExposedRoleRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_exposed_role_with_casting_by_form_id(self, form_id):
        """Recibe el id de un form. Obtiene la información del rol expuesto que tiene asociado y el casting
        al que pertenece ese rol. Devuelve un diccionario con la información obtenida usando como clave los nombres
        de los campos que corresponden para cada dato."""
        result =  self.db.query(models.ExposedRole.has_limited_spots, models.ExposedRole.spots_amount, 
                models.ExposedRole.occupied_spots, models.CastingCall.title, 
                models.CastingCall.publication_date, models.CastingCall.state, models.CastingCall.id, 
                models.ExposedRole.id).\
                join(models.CastingCall, models.ExposedRole.casting_call_id == models.CastingCall.id).\
                filter(models.ExposedRole.form_id == form_id).first()

        if result:
            data_with_columns = {
                'has_limited_spots': result[0],
                'spots_amount': result[1],
                'occupied_spots': result[2],
                'casting_call_title': result[3],
                'casting_call_publication_date': result[4],
                'casting_call_state': result[5],
                'casting_call_id': result[6],
                'exposed_role_id': result[7]
            }

        return data_with_columns
    
    def update_occupied_spots(self, exposed_role_id, occupied_spots):
        self.db.query(models.ExposedRole).filter(models.ExposedRole.id == exposed_role_id).\
        update({'occupied_spots': occupied_spots})
        self.db.commit()