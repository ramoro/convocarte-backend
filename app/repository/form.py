import models
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

class FormRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_form_by_id(self, form_id):
        form = (
            self.db.query(models.Form)
            .filter(models.Form.id == form_id)
            .options(joinedload(models.Form.form_fields))  # Carga los campos asociados
            .first()
        )

        return form

    def get_form_by_user_id_and_title(self, user_id, title):
        return self.db.query(models.Form).filter(
            and_(
                models.Form.owner_id == user_id,
                models.Form.form_title == title
            )).first()

    def update_form(self, form_data):
        try:

            # Obtener el form existente
            form = self.db.query(models.Form).filter(models.Form.id == form_data.id).first()

            if not form:
                return None, "Not Found Error" 

            # Actualizar titulo del form
            form.form_title = form_data.form_title

            #Se limpian los campos existentes
            self.db.query(models.FormField).filter(models.FormField.form_id == form.id).delete()

            # Agrega los nuevos campos
            for field in form_data.form_fields:
                new_field = models.FormField(
                    form_id=form.id,
                    title=field.title,
                    type=field.type,
                    order=field.order,
                    is_required=field.is_required
                )
                self.db.add(new_field)

            self.db.commit()
            return form, ""
        
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None, "Database Error"