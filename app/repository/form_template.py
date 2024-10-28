import models
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
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



