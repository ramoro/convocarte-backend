from datetime import datetime, timezone
import models
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import date

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
            #Y luego se agrega la informacion del rol expuesto en OpenRole
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
                if role['has_limited_spots']:
                    role['occupied_spots'] = 0
                new_role = models.OpenRole(**role)
                self.db.add(new_role)

            self.db.commit()
            self.db.refresh(new_casting_call) 
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None
        
        return new_casting_call
    
    def get_casting_calls_by_user_id(self, user_id):
        return self.db.query(models.CastingCall).\
            filter(and_(models.CastingCall.owner_id == user_id,
                        models.CastingCall.deleted_at == None)).all()
    
    def update_casting_call(self, casting_call_id, updated_casting_call):
        casting_call_query = self.db.query(models.CastingCall).\
                            filter(models.CastingCall.id == casting_call_id)

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
                joinedload(models.CastingCall.open_roles)
                .joinedload(models.OpenRole.role),  # Cargar el role de cada open role
                joinedload(models.CastingCall.open_roles)
                .joinedload(models.OpenRole.form)   # Cargar el form de cada open role
            )  
            .first()
        )
    
        return casting_call

    def update_casting_call_with_open_roles(self, casting_call_id, updated_casting_call, updated_roles, 
                                               deleted_photos_names, new_photos_names):
        """Recibe el id de un casting, un diccionario con los datos actualizados del casting, la lista de los roles 
        expuestos actualizados (cada uno es un diccionario con su data), una lista con los nombres de las fotos eliminadas 
        (y sus extensiones) y otra con los nombres de las nuevas fotos generadas. Actualiza el casting y sus roles expuestos 
        asociados. Devuelve el casting actualizado, o None si no se encontro un casting con el id recibido."""

        try:
            # Obtener el casting existente
            casting_call_query = self.db.query(models.CastingCall).\
                                filter(models.CastingCall.id == casting_call_id)
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
                self.db.query(models.OpenRole).\
                filter(models.OpenRole.id == role['id']).update(role, synchronize_session=False)

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
            casting_call_query = self.db.query(models.CastingCall).\
                                filter(models.CastingCall.id == casting_call_id)
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

    def get_published_casting_calls(self, casting_filters):
        try:
            query = self.db.query(models.CastingCall).filter(
                and_(
                    models.CastingCall.state == "Publicado",  # Solo castings publicados
                    models.CastingCall.deleted_at == None  # No eliminados
                )
                # Cargar projecto y roles asociados a CastingCall:
            ).options(joinedload(models.CastingCall.project), joinedload(models.CastingCall.open_roles))  

            # Filtrar por date_order (Ascendente o Descendente)
            if casting_filters.date_order == "Ascendente":
                query = query.order_by(models.CastingCall.publication_date.asc())
            elif casting_filters.date_order == "Descendente":
                query = query.order_by(models.CastingCall.publication_date.desc())

            # Si trae filtro de edad, filtrar por edad, teniendo en cuenta
            # que el rango de edad puede ser abierto (min_age_required con valor y max_age_required None, o viceversa)
            # tambien agarra los castings que no setearon filtro de edad
            if casting_filters.age is not None:
                query = query.filter(
                    models.CastingCall.open_roles.any(
                        and_(
                            models.OpenRole.disabled == False, #El rol a evaluar debe estar habilitado
                            or_(
                                and_(models.OpenRole.min_age_required <= casting_filters.age, models.OpenRole.max_age_required >= casting_filters.age),
                                and_(models.OpenRole.min_age_required <= casting_filters.age, models.OpenRole.max_age_required == None),
                                and_(models.OpenRole.min_age_required == None, models.OpenRole.max_age_required >= casting_filters.age),
                                and_(models.OpenRole.min_age_required == None, models.OpenRole.max_age_required == None)
                            )
                        )

                    )
                )

            # Si trae filtro de altura, idem que por edad
            if casting_filters.height is not None:
                query = query.filter(
                    models.CastingCall.open_roles.any(
                        and_(
                            models.OpenRole.disabled == False, #El rol a evaluar debe estar habilitado
                            or_(
                                and_(models.OpenRole.min_height_required <= casting_filters.height, models.OpenRole.max_height_required >= casting_filters.height),
                                and_(models.OpenRole.min_height_required <= casting_filters.height, models.OpenRole.max_height_required == None),
                                and_(models.OpenRole.min_height_required == None, models.OpenRole.max_height_required >= casting_filters.height),
                                and_(models.OpenRole.min_height_required == None, models.OpenRole.max_height_required == None)
                            )
                        ) 
                    )
                )

            # Filtrar por remuneration_types (cadena de texto con valores separados por comas)
            if casting_filters.remuneration_types:
                query = query.filter(
                    models.CastingCall.remuneration_type.in_(casting_filters.remuneration_types)
                )

            # Filtrar por categories (cadena de texto con valores separados por comas)
            if casting_filters.categories:
                query = query.join(models.CastingCall.project).filter(
                    models.Project.category.in_(casting_filters.categories)
                )

            # Filtrar por hair_colors dentro de los roles (donde hair_colors_required es una cadena separada por comas)
            # Me fijo que 
            if casting_filters.hair_colors:
                #Creo una condicion or para obtener cualquier casting que dentro suyo tenga aunque sea un rol con al menos un color
                #de pelo que coincida con los colores de pelo que vienen en la lista de filtro casting_filters.hair_colors
                or_conditions = []
                for hair_color in casting_filters.hair_colors:
                    or_conditions.append(
                        models.OpenRole.hair_colors_required.ilike(f"%{hair_color}%")
                    )
                
                query = query.filter(
                    models.CastingCall.open_roles.any(
                        and_(
                            models.OpenRole.disabled == False,  # El rol a evaluar debe estar habilitado
                            or_(*or_conditions,
                                models.OpenRole.hair_colors_required == "", # si casting no trae filtro de pelos, se devuelve tambien
                                models.OpenRole.hair_colors_required == None)  
                        )
                    )
                )
           
            casting_calls = query.all()

            return casting_calls
        except Exception as e:
            print(f"Error occurred: {e}") 
            return None
        
    def delete_casting_call(self, casting_call_id):
        try:
            casting_call = self.db.query(models.CastingCall).\
                filter(models.CastingCall.id == casting_call_id).first()
            if casting_call:
                # Se eliminan los roles expuestos en el casting y sus
                # forms generados
                for open_role in casting_call.open_roles:
                    if open_role.form:
                        open_role.form.deleted_at = datetime.now(timezone.utc)
                        self.db.add(open_role.form)
                    
                    open_role.deleted_at = datetime.now(timezone.utc)
                    self.db.add(open_role)
                # Marco el CastingCall como eliminado con la fecha
                # pero no lo borro de la bdd para tenerlo como historial
                casting_call.deleted_at = datetime.now(timezone.utc)
                casting_call.state = "Eliminado"
                self.db.add(casting_call)

                self.db.commit()
                return True
            else:
                return False
        except Exception as e:
            print(e)
            self.db.rollback()
            return False
        
    def get_casting_call_by_id_with_postulations(self, casting_call_id, current_user_id):
        """Recibe el id de un casting y el id del usuario que solicitó la información, y devuelve toda
        la data del casting (roles asociados, forms, proyecto), pero ademas devuelve el listado de postulaciones
        hechas para ese casting con la información de si tienen mensajes sin leer, y cuantos."""
        casting_call = (
            self.db.query(models.CastingCall)
            .filter(models.CastingCall.id == casting_call_id)
            .options(
                joinedload(models.CastingCall.project),
                joinedload(models.CastingCall.open_roles)
                .joinedload(models.OpenRole.role),  # Cargar el role de cada open role
                joinedload(models.CastingCall.open_roles)
                .joinedload(models.OpenRole.form),   # Cargar el form de cada open role
                joinedload(models.CastingCall.open_roles)
                .joinedload(models.OpenRole.casting_postulations) # Cargar postulaciones de cada open role
                .joinedload(models.CastingPostulation.messages) #Cargar mensajes de cada postulacion para saber si hay mensajes sin leer
            )  
            .first()
        )

        if casting_call:
            # Procesar cada postulación para agregar info de mensajes no leídos
            for open_role in casting_call.open_roles:
                for postulation in open_role.casting_postulations:
                    # Contar mensajes no leídos donde el emisor no es el usuario actual
                    unread_count = sum(
                        1 for message in postulation.messages 
                        if "Sin Leer" in message.state 
                        and message.sender_id != current_user_id
                    )

                    postulation.unread_messages_count = unread_count
                    postulation.has_unread_messages = unread_count > 0
    
        return casting_call

    def update_expired_casting_calls(self):
        today = date.today()

        expired_castings_query = self.db.query(models.CastingCall)\
        .filter(models.CastingCall.expiration_date <= today)\
        .filter(models.CastingCall.state != "Vencido")
        expired_castings = expired_castings_query.all()
        expired_castings_query.update({models.CastingCall.state: "Vencido"}, synchronize_session=False)

        self.db.commit()

        return expired_castings
