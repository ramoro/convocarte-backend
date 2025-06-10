import models
from sqlalchemy.orm import Session
from sqlalchemy import func

class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email):
        return self.db.query(models.User).filter((models.User.email == email)).first()
    
    def get_user_by_id(self, id):
        return self.db.query(models.User).filter(models.User.id == id).first() #Se usa first y no all porque se sabe q por id es unico, sino seguiria buscando y gastaria mas tiempo
    
    def add_new_user(self, dict_user):
        new_user = models.User(
            #username=user.username, fullname=user.fullname, email=user.email, 
            #password=user.password
            **dict_user) #Pasamos el modelo de pydantic a diccionario y luego lo desempaquetamos
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user) #devuelve lo que se guardo recien y se almacena en new_user

        return new_user
    
    def update_user(self, id, data):
        self.db.query(models.User).filter(models.User.id == id).update(data, synchronize_session=False)
        self.db.commit()

    def delete_user(self, user):
        
        # Elimina físicamente los form_templates y sus form_template_fields asociados al usuario
        for template in user.form_templates:
            self.db.query(models.FormTemplateField).filter(models.FormTemplateField.form_template_id == template.id).delete()
        self.db.query(models.FormTemplate).filter(models.FormTemplate.owner_id == user.id).delete()

        now = func.now()

        # Soft-delete de Forms y sus FormFields (relacionados a casting_calls del user)
        forms = (
            self.db.query(models.Form)
            .join(models.Form.casting_call)
            .filter(models.Form.casting_call.has(owner_id=user.id))
            .all()
        )
        for form in forms:
            form.deleted_at = now
            for field in form.form_fields:
                field.deleted_at = now

        #Soft-delete de CastingCalls del usuario y sus roles abiertos asociados
        for casting in user.casting_calls:
            for open_role in casting.open_roles:
                open_role.deleted_at = now
            casting.deleted_at = now
            casting.state = "Eliminado"

        for postulation in user.casting_postulations:
            postulation.deleted_at = now
            postulation.state = "Eliminada"

        # Soft-delete de Projects del usuario
        for project in user.projects:
            project.deleted_at = now
            for role in project.roles:
                role.deleted_at = now

        user.deleted_at = now

        self.db.commit()

