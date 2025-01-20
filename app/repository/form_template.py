import models
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

class FormTemplateRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_form_template_by_user_id_and_title(self, user_id, title):
        return self.db.query(models.FormTemplate).filter(
            and_(
                models.FormTemplate.owner_id == user_id,
                models.FormTemplate.form_template_title == title
            )).first()
    
    def add_new_form_template(self, user_id, title, form_template_fields):
        """Recibe el id del usuario, el titulo del formulario y una lista con los campos que posee
        el template. Agrega el formulario en la tabla FormTemplates y cada campo con el formulario
        asociado en la tabla FormTemplateFields. Devuelve el template almacenado o devuelve None en
        caso de error."""
        try:
            new_template = models.FormTemplate(owner_id=user_id, form_template_title=title)

            self.db.add(new_template)
            self.db.flush() #Asi ya la variable se actualiza con el id generado para el template

            for field in form_template_fields:
                form_field = models.FormTemplateField(
                    form_template_id=new_template.id,
                    title=field.title,
                    type=field.type,
                    order=field.order,
                    is_required=field.is_required,
                )
                self.db.add(form_field)

            self.db.commit()
            self.db.refresh(new_template) 
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None
        
        return new_template
    
    def get_form_templates_by_user_id(self, user_id):
        return self.db.query(models.FormTemplate).filter((models.FormTemplate.owner_id == user_id)).all()

    def get_form_template_by_id(self, form_template_id):
        form_template = (
            self.db.query(models.FormTemplate)
            .filter(models.FormTemplate.id == form_template_id)
            .options(joinedload(models.FormTemplate.form_template_fields))  # Carga los campos asociados
            .first()
        )

        return form_template
    
    def delete_form_template(self, form_template_id: int):
        error= ""
        try:
            form_template = self.db.query(models.FormTemplate).\
            filter(models.FormTemplate.id == form_template_id).first()
            
            if form_template:
                # Eliminar todos los campos asociados en una sola consulta
                self.db.query(models.FormTemplateField).\
                filter(models.FormTemplateField.form_template_id == form_template_id).delete(synchronize_session='fetch')

                # Eliminar el formulario
                self.db.delete(form_template)
                self.db.commit() 
                return True, error
            error = "Not Found Error"
            return False, error
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            error = "Database Error"
            print(f"Error occurred: {e}") 
            return False, error
        
    def update_form_template(self, form_template_data):
        try:

            # Obtener el form template existente
            form_template = self.db.query(models.FormTemplate).\
            filter(models.FormTemplate.id == form_template_data.id).first()

            if not form_template:
                return None, "Not Found Error" 

            # Actualizar titulo del form
            form_template.form_template_title = form_template_data.form_template_title

            #Se limpian los campos existentes
            self.db.query(models.FormTemplateField).\
            filter(models.FormTemplateField.form_template_id == form_template.id).delete()

            # Agrega los nuevos campos
            for field in form_template_data.form_template_fields:
                new_field = models.FormTemplateField(
                    form_template_id=form_template.id,
                    title=field.title,
                    type=field.type,
                    order=field.order,
                    is_required=field.is_required
                )
                self.db.add(new_field)

            self.db.commit()
            return form_template, ""
        
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None, "Database Error"
