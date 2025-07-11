import models
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime, timezone

class ProjectRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_project_by_user_id_and_title(self, user_id, project_name):
        return self.db.query(models.Project).filter(
            and_(
                models.Project.owner_id == user_id,
                models.Project.name == project_name,
                models.Project.deleted_at == None
            )).first()
    
    def add_new_project(self, dict_project, roles):
        """Recibe un diccionario con los datos de un proyecto y una lista de diccionarios, cada uno
        con la información de un rol perteneciente al prouecto. Agrega el proyecto en la tabla Projects
        y cada rol con el proyecto asociado en la tabla Roles. Devuelve el proyecto almacenado o None en caso 
        contrario."""
        try:
            new_project = models.Project(**dict_project) 

            self.db.add(new_project)
            self.db.flush() #Asi ya la variable se actualiza con el id generado para el proyecto

            for role in roles:
                new_role = models.Role(
                    project_id=new_project.id,
                    name=role.name,
                    description=role.description
                )
                self.db.add(new_role)

            self.db.commit()
            self.db.refresh(new_project) 
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None
        
        return new_project
    
    def get_projects_by_user_id(self, user_id):
        return self.db.query(models.Project).filter(and_(models.Project.owner_id == user_id, 
                                                    models.Project.deleted_at == None)).all()
    
    def get_user_projects_with_roles(self, user_id):
        projects = self.db.query(models.Project).\
        filter(and_(models.Project.owner_id == user_id, models.Project.deleted_at == None)).\
        options(joinedload(models.Project.roles)).all()

        return projects
    
    def get_project_by_id(self, project_id):
        return self.db.query(models.Project).filter(and_(models.Project.id == project_id, 
                                                    models.Project.deleted_at == None)).first()
    
    def delete_project(self, project_id):
        try:
            #Primero se eliminan todos los castings que estan asociados 
            # al proyecto (en teoria deberian estar todos finalizados)
            associated_castings = self.db.query(models.CastingCall).\
            filter((models.CastingCall.project_id == project_id)).all()
            
            for casting in associated_castings:
                casting.deleted_at = datetime.now(timezone.utc)
                self.db.add(casting)
            
            project = self.get_project_by_id(project_id)

            if project:
                # Marcar los roles asociados al proyecto como eliminados
                self.db.query(models.Role).filter(models.Role.project_id == project.id).update(
                    {models.Role.deleted_at: datetime.now(timezone.utc)}, synchronize_session='fetch')
                
                # Marcar el proyecto como eliminado
                project.deleted_at = datetime.now(timezone.utc)
                self.db.add(project)

                self.db.commit()
                return True
            return False
        except:
            self.db.rollback()
            return False
        
    def get_project_by_user_id_and_name(self, user_id, name):
        return self.db.query(models.Project).filter(
            and_(
                models.Project.owner_id == user_id,
                models.Project.name == name,
                models.Project.deleted_at == None
            )).first()
    
    def update_project(self, project_id, updated_project, roles):
        """Recibe el id del proyecto a actualizar, un diccionario con los datos actualizados del proyecto y
        una lista de diccionarios con cada rol y su nueva informacion. Actualiza estos datos nuevos y devuelve
        el proyecto actualizado, o None en caso de error."""
        try:
            project_query = self.db.query(models.Project).filter(and_(models.Project.id == project_id, 
                                                                      models.Project.deleted_at == None))

            if not project_query.first():
                return None

            project_query.update(updated_project, synchronize_session=False)

            #Se limpian los roles existentes y se reemplazan por nuevos
            self.db.query(models.Role).filter(and_(models.Role.project_id == project_id,
                                                   models.Role.deleted_at == None)).delete()

            for role in roles:
                if "description" not in role:
                    role["description"] = None

                updated_role = models.Role(
                    name=role["name"] ,
                    project_id=project_id,
                    description=role["description"] 
                )
                self.db.add(updated_role)

            self.db.commit()
            return updated_project
        
        except Exception as e:
            self.db.rollback()  # Rollbackea si algo falla
            print(f"Error occurred: {e}") 
            return None

    def update_project_state(self, project):
        """Recibe una entidad projecto, revisa si tiene algun casting publicado y en ese
        caso se setea como que esta siendo usado. Caso contrario is_used se pasa a false."""
        is_used = False
        for casting_call in project.casting_calls:
            if casting_call.state == "Publicado":
                is_used = True
        project.is_used = is_used
        print(project.is_used)

        self.db.commit()
        return

    def get_project_with_roles_and_castings_by_id(self, project_id):
        project = (
            self.db.query(models.Project)
            .options(
                joinedload(models.Project.roles),
                joinedload(models.Project.casting_calls)
            )
            .filter(
                and_(
                    models.Project.id == project_id,
                    models.Project.deleted_at == None
                )
            )
            .first()
        )

        if not project:
            return None

        # Procesar los roles para incluir el nombre del usuario asignado
        roles_with_assignee = []
        for role in project.roles:
            assigned_user_name = None
            if role.assigned_user_id:
                assigned_user = self.db.query(models.User).filter(
                    models.User.id == role.assigned_user_id
                ).first()
                assigned_user_name = assigned_user.fullname if assigned_user else None

            role_data = {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "assigned_user_name": assigned_user_name,
            }
            roles_with_assignee.append(role_data)

        # Procesar los casting calls
        castings = []
        for casting in project.casting_calls:
            if casting.deleted_at is None:
                castings.append({
                    "id": casting.id,
                    "title": casting.title,
                    "state": casting.state,
                    "publication_date": casting.publication_date,
                    "expiration_date": casting.expiration_date,
                })

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "category": project.category,
            "region": project.region,
            "is_used": project.is_used,
            "created_at": project.created_at,
            "owner_id": project.owner_id,
            "roles": roles_with_assignee,
            "castings": castings
        }