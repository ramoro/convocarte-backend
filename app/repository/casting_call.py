import models
from sqlalchemy.orm import Session, joinedload, subqueryload
from sqlalchemy import and_

class CastingCallRepository:

    def __init__(self, db: Session):
        self.db = db

    def add_new_casting_call(self, casting_call, casting_roles):
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
            #Y luego se agrega la realacion a RoleByCastingCall
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
                print(role)
                new_role = models.ExposedRole(**role)
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

        

