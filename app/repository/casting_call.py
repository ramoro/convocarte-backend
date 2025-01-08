import models
from sqlalchemy.orm import Session, joinedload, subqueryload
from sqlalchemy import and_

class CastingCallRepository:

    def __init__(self, db: Session):
        self.db = db

    def add_new_casting_call(self, casting_call, casting_roles, associated_project):
        """Recibe un diccionario con los datos del casting y otro diccionario con
        los datos del rol junto a el Form Template que se usara para generar el Form y sus 
        Fields que tendra el rol para que se pueda aplicar a el. Almacena para cada Rol
        el Form y sus Form Fields generados, junto con la relacion que se establece entre el rol, el casting y 
        el template en la tabla RoleByCastingCall. Y se crea tambien el casting. Se devuelve la instancia generada
        para esta entidad."""
        try:
            #Se crea Casting Call
            new_casting_call = models.CastingCall(**casting_call) 

            self.db.add(new_casting_call)
            self.db.flush() #Asi ya la variable se actualiza con el id generado para el casting

            #Por cada rol se crea un Form y sus FormFields a partir de un Form Template
            #Y luego se agrega la informacion del rol expuesto en ExposedRole
            for role in casting_roles:
                form_template_associated = role['form_template']
                #Se crea primero el Form y
                form = models.Form(role_id=role['role_id'], 
                                casting_call_id=new_casting_call.id, 
                                form_title=form_template_associated.form_template_title)
                self.db.add(form)
                self.db.flush()

                for template_field in form_template_associated.form_template_fields:
                    form_field = models.FormField(
                        form_id=form.id,
                        title=template_field.title,
                        type=template_field.type,
                        order=template_field.order,
                        is_required=template_field.is_required
                    )
                    self.db.add(form_field)
                    self.db.flush()

                role['casting_call_id'] = new_casting_call.id
                #Sacamos el modelo de form template del diccionario y le agregamos el id
                #del form generado
                role.pop('form_template') 
                role['form_id'] = form.id
                new_role = models.ExposedRole(**role)
                self.db.add(new_role)

            #Se actualiza el proyecto asociado con su nuevo estado
            associated_project.is_used = True

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
    
        # Retorna el registro actualizado
        return casting_call_query.first()
    
    def get_casting_call_by_title_and_state(self, casting_call_title, state):
        
        return self.db.query(models.CastingCall).filter(and_(
            models.CastingCall.title == casting_call_title,
            models.CastingCall.state == state
        )).first()
    
    def get_casting_call_by_id(self, casting_call_id):
        """Recibe el id de un casting y devuelve toda su informacion, junto con la info de cada
        rol asociado y cada form adjudicado a cada rol, y junto al projecto que tiene asociado"""
        casting_call = (
            self.db.query(models.CastingCall)
            .filter(models.CastingCall.id == casting_call_id)
            .options(
                joinedload(models.CastingCall.project),
                joinedload(models.CastingCall.exposed_roles)
                .joinedload(models.ExposedRole.role),  # Cargar el role de cada exposed role
                joinedload(models.CastingCall.exposed_roles)
                .joinedload(models.ExposedRole.form)   # Cargar el form de cada exposed role
            )  
            .first()
        )
    
        return casting_call

    def update_casting_call_with_exposed_roles(self, casting_call_id, updated_casting_call, updated_roles, 
                                               deleted_photos_names, new_photos_names):
        """Recibe el id de un casting, un diccionario con los datos actualizados del casting, la lista de los roles 
        expuestos actualizados (cada uno es un diccionario con su data), una lista con los nombres de las fotos eliminadas 
        (y sus extensiones) y otra con los nombres de las nuevas fotos generadas. Actualiza el casting y sus roles expuestos 
        asociados. Devuelve el casting actualizado, o None si no se encontro un casting con el id recibido."""

        try:
            # Obtener el casting existente
            casting_call_query = self.db.query(models.CastingCall).filter(models.CastingCall.id == casting_call_id)
            current_casting_call = casting_call_query.first()
            if not current_casting_call:
                return None, f"Casting call with id {casting_call_id} not found." 

            #Obtiene del casting actual las fotos, elimina las correspondientes y agrega las nuevas
            separated_casting_photos = []
            if current_casting_call.casting_photos: 
                separated_casting_photos = separated_casting_photos = current_casting_call.casting_photos.split(',')

            for photo in deleted_photos_names:
                separated_casting_photos.remove(photo)
            
            for photo in new_photos_names:
                if photo: separated_casting_photos.append(photo)

            updated_casting_call['casting_photos'] = ','.join(separated_casting_photos)
            casting_call_query.update(updated_casting_call, synchronize_session=False)

            #Actualiza los roles expuestos
            for role in updated_roles:
                self.db.query(models.ExposedRole).filter(models.ExposedRole.id == role['id']).update(role, synchronize_session=False)

            self.db.commit()
            return updated_casting_call, ""
        
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None, "Database Error"
        
    def finish_casting_call(self, casting_call_id, updated_casting_call):
        """Recibe el id del casting y el casting ya actualizado. Actualiza el proyecto que tiene asociado en estado
        de Sin uso en caso de que el proyecto no haya quedado usado en otro casting. Devuelve el casting actualizado."""
        try:
            casting_call_query = self.db.query(models.CastingCall).filter(models.CastingCall.id == casting_call_id)
            casting_call = casting_call_query.first()
            
            if not casting_call:
                return None, "Not Found"
            
            project = casting_call.project

            # Verificar si el proyecto tiene más castings asociados que no han sido finalizados
            other_castings = self.db.query(models.CastingCall).filter(and_(
                models.CastingCall.project_id == project.id,
                models.CastingCall.state != "Finalizado"
            )).all()

            # Si no hay más castings que contengan el proyecto, actualizar el campo is_used del proyecto a False
            if len(other_castings) == 1:  # Si solo hay un casting asociado (este)
                project.is_used = False
                self.db.add(project)  

            casting_call_query.update(updated_casting_call, synchronize_session=False)
            self.db.commit()

        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None, "Database Error"
        
        return casting_call, None
