from typing import List
from fastapi import HTTPException, Depends, APIRouter, Form, Response
from database import get_db
from starlette import status
from sqlalchemy.orm import Session
import oauth2
import models
from schemas.casting_call import  ( 
    CastingCallPreviewResponse, 
    CastingCallPublication, 
    PublishedCastingCallResponse, 
    CastingCallChangeState, 
    CastingCallResponse,
    CastingCallFilter,
)
from repository.casting_call import CastingCallRepository
from repository.project import ProjectRepository
from repository.role import RoleRepository
from repository.form_template import FormTemplateRepository
from fastapi import File, UploadFile
from config import settings
import json
import pytz
from datetime import datetime
from storage_managers.local_storage_manager import LocalStorageManager
from storage_managers.cloud_storage_manager import CloudStorageManager, CLOUD_STORAGE_URL

# Defino el almacenamiento segun si es corrida local o no (si no es local los archivos se almacenan en Google Drive)
if "localhost" in settings.backend_url:
    storage_manager = LocalStorageManager()
else:
    storage_manager = CloudStorageManager() 


router = APIRouter(
    prefix="/casting-calls", 
    tags=["CastingCalls"],
    dependencies=[Depends(oauth2.get_current_user)]
)

def add_path_to_photo(casting_call):
    """Recibe un casting y si tiene fotos le agrega el path correspondiente para poder acceder desde el front.
    El path varia si se esta corriendo local, o si se esta corriendo en produccion (ahi usa paths de google drive)"""
    if casting_call.casting_photos:
        #Si es corrida local uso el path local, sino la url para descargar desde google drive
        if "localhost" in settings.backend_url:
            #Se hace un split y se le agrega a cada photo el path donde se ubica localmente
            photos_with_paths = list(map(
                lambda photo_name : settings.backend_url + settings.casting_call_photos_path[1:] + photo_name,
                casting_call.casting_photos.split(",")
                ))
        else:
            #Para el caso de google drive, se saca la extension de la foto, quedando solo el nombre, que es el id que tiene en el google drive
            photos_with_paths = list(map(
                lambda photo_name : CLOUD_STORAGE_URL + photo_name.split('.')[0], 
                casting_call.casting_photos.split(",")
                ))
        
        casting_call.casting_photos = photos_with_paths
    else:
        casting_call.casting_photos = []

async def store_casting_photos(new_casting_call_photos):
    """Recibe una lista de files que representan fotos del casting. Recorre esta lista y almacena cada foto.
    Devuelve un string con los nombres generados para almacenar las fotos, separados por comas."""
    new_photos_names = ""
    filepath = settings.casting_call_photos_path
    for photo_file in new_casting_call_photos:

        filename = photo_file.filename
        extension = filename.split(".")[-1].lower()

        if extension not in ["png", "jpg", "jpeg"]:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Photo {filename} with not allowed file extension.")
        
        #TODO: eliminar fotos almacenadas si falla add_new_casting_call del repository
        name_to_store, file_url = await storage_manager.store_file(extension, 
                                                                   filepath, 
                                                                   photo_file, 
                                                                   True, 600, 650)
        
        new_photos_names += name_to_store + ","
    new_photos_names = new_photos_names[:-1] #Elimino la coma del final

    return new_photos_names

# El str de la lista casting_roles vendra de la forma:
# {"role_id":1,"form_template_id":1,"min_age_required":25,"max_age_required":35,"additional_requirements":"",
# "has_limited_spots":false}
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_casting_call(title: str = Form(...),
                        description: str = Form(None),
                        project_id: int = Form(...),
                        remuneration_type: str = Form(...),
                        casting_roles: List[str] = Form(...),
                        casting_call_photos: List[UploadFile] = File(None), 
                        current_user: models.User = Depends(oauth2.get_current_user), 
                        db: Session = Depends(get_db)):

    casting_call_repository = CastingCallRepository(db)
    project_repository = ProjectRepository(db)
    role_repository = RoleRepository(db)
    form_template_repository = FormTemplateRepository(db)

    if not casting_call_photos: casting_call_photos = []

    #Validamos que haya enviado entidades que existen en la bdd
    associated_project = project_repository.get_project_by_id(project_id)
    
    if not associated_project:
        raise HTTPException(status_code=404, 
                            detail=f"Project with id {project_id} not found.")

    #Validacion y armado de lista de roles
    roles_list = []
    for role_data in casting_roles:
        role = json.loads(role_data)
        
        #Validacion de campos requeridos por cada rol
        if not role.get('role_id'):
            raise HTTPException(status_code=400, 
                                detail="role_id is required for each role.")
    
        if not role.get('form_template_id'):
            raise HTTPException(status_code=400, 
                                detail="Form template is required for each role. Every role needs the field form_template.")
        
        #Validacion de ids existentes en la bdd
        if not role_repository.get_role_by_id(role["role_id"]):
            raise HTTPException(status_code=404, 
                                detail=f"Role with id {role['role_id']} not found.")
        form_template = form_template_repository.get_form_template_by_id(role["form_template_id"])

        if not form_template:
            raise HTTPException(status_code=404, 
                                detail=f"Form template with id {role['form_template_id']} not found.")
        
        # Agregamos al diccionario con la info del rol el modelo de Form Template para que despues se use para crear
        # el Form con su misma info.
        role["form_template"] = form_template
        role.pop("form_template_id")
        roles_list.append(role)

    #Almacenamiento de fotos y armado de string con nombres generados en hexa para las fotos
    photos_names = await store_casting_photos(casting_call_photos)

    #Almacenamiento del casting en la bdd junto con sus roles
    new_casting_call = {"title": title, 
                        "description": description, 
                        "project_id": project_id,
                        "remuneration_type": remuneration_type,
                        "owner_id": current_user.id,
                        "casting_photos": photos_names,
                        "state": "Borrador"} #Arranca en estado Borrador hasta que se publique
    
    # Se le manda los datos del casting recibidos sumado al id del usuario que lo creo 
    # y por otro lado la lista de roles que expondra el casting
    casting_call_created = casting_call_repository.add_new_casting_call(new_casting_call, 
                                                                        roles_list, associated_project)
    if not casting_call_created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An error occurred while creating the casting call")
    
    return {'success': True, 'status_code': status.HTTP_201_CREATED,
            'casting_call_title': title, 'casting_call_id': casting_call_created.id }

@router.get("/", response_model=List[CastingCallPreviewResponse])
def get_user_casting_calls(current_user: models.User = Depends(oauth2.get_current_user), 
                        db: Session = Depends(get_db)):
    
    casting_call_repository = CastingCallRepository(db)

    my_casting_calls = casting_call_repository.get_casting_calls_by_user_id(current_user.id)

    for casting_call in my_casting_calls:
        add_path_to_photo(casting_call)
    
    return my_casting_calls

@router.post("/published", response_model=List[CastingCallPreviewResponse])
def search_of_published_casting_calls(casting_filters: CastingCallFilter, 
                        db: Session = Depends(get_db)):
    
    casting_call_repository = CastingCallRepository(db)

    casting_calls = casting_call_repository.get_published_casting_calls(casting_filters)

    if casting_calls is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    #TODO: Almacenar photos con path (local o drive segun ambiente) 
    # para no tener que setearselo cada vez que pido los castings
    for casting_call in casting_calls:
        add_path_to_photo(casting_call)
    
    return casting_calls

@router.patch("/publish/{casting_id}")
def publish_casting_call(casting_id: int, casting_call: CastingCallPublication,  
                         db: Session = Depends(get_db)) -> PublishedCastingCallResponse:
    
    if casting_call.state == "Finalizado":
        raise HTTPException(status_code=400,
                             detail="The casting cannot be published because it has already ended.")

    casting_call_repository = CastingCallRepository(db)

    #Se valida que no exista un casting publicado con el mismo nombre
    existing_published_casting = casting_call_repository.get_casting_call_by_title_and_state(casting_call.title, "Publicado")
    if existing_published_casting:
        raise HTTPException(status_code=400, 
                            detail=f"The casting cannot be published because there is already a published casting with the title {casting_call.title}")

    #Le seteo la fecha de publicacion con la fecha actual
    casting_call_dict = casting_call.model_dump()
    argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
    casting_call_dict['publication_date'] = datetime.now(argentina_tz).date()

    #Le seteo el nuevo estado al casting (Publicado)
    casting_call_dict['state'] = "Publicado"

    updated_casting_call = casting_call_repository.update_casting_call(casting_id, casting_call_dict)

    if not updated_casting_call:
        raise HTTPException(status_code=404, 
                            detail=f"Casting call with id {casting_id} not found.")

    return updated_casting_call

@router.patch("/pause/{casting_id}")
def stop_casting_call(casting_id: int, casting_call: CastingCallChangeState,
                         db: Session = Depends(get_db)) -> CastingCallChangeState:
    
    if casting_call.state == "Finalizado":
        raise HTTPException(status_code=400, 
                            detail="The casting cannot be paused because it has already ended.")
    elif casting_call.state == "Borrador":
        raise HTTPException(status_code=400, 
                            detail="The casting cannot be paused because it hasn't been published yet.")

    casting_call_repository = CastingCallRepository(db)

    casting_call_dict = casting_call.model_dump()

    #Le seteo el nuevo estado al casting (Pausado)
    casting_call_dict['state'] = "Pausado"

    updated_casting_call = casting_call_repository.update_casting_call(casting_id, casting_call_dict)

    if not updated_casting_call:
        raise HTTPException(status_code=404, 
                            detail=f"Casting call with id {casting_id} not found.")

    return updated_casting_call

@router.patch("/finish/{casting_id}")
def finish_casting_call(casting_id: int, casting_call: CastingCallChangeState, 
                         db: Session = Depends(get_db)) -> CastingCallChangeState:
    
    if casting_call.state == "Borrador":
        raise HTTPException(status_code=400, 
                            detail="The casting cannot be finished because it hasn't been published yet.")

    casting_call_repository = CastingCallRepository(db)

    casting_call_dict = casting_call.model_dump()

    #Le seteo el nuevo estado al casting (Pausado)
    casting_call_dict['state'] = "Finalizado"

    updated_casting_call, error_message = casting_call_repository.finish_casting_call(casting_id, casting_call_dict)

    if not updated_casting_call:
        if "Not Found" in error_message:
            raise HTTPException(status_code=404, 
                                detail=f"Casting call with id {casting_id} not found.")
        else:
            raise HTTPException(status_code=500, 
                                detail="Internal Server Error")

    return updated_casting_call

@router.get("/{casting_id}")
def get_casting_call(casting_id: int, 
                        db: Session = Depends(get_db)) -> CastingCallResponse:
    
    casting_call_repository = CastingCallRepository(db)
    casting_call = casting_call_repository.get_casting_call_by_id(casting_id)

    if not casting_call:
        raise HTTPException(status_code=404, detail=f"Casting call with id {casting_id} not found.")
    
    add_path_to_photo(casting_call)
    
    return casting_call

@router.patch("/{casting_id}", status_code=status.HTTP_200_OK)
async def update_casting_call(casting_id: int,
                        casting_state: str = Form(...),
                        title: str = Form(...),
                        description: str = Form(None),
                        project_id: int = Form(...),
                        remuneration_type: str = Form(...),
                        casting_roles: List[str] = Form(...),
                        #Viene con un str con el url de cada photo separadas por comas:
                        deleted_casting_call_photos: str = Form(None), 
                        added_casting_call_photos: List[UploadFile] = File(None),
                        db: Session = Depends(get_db)):
    
    casting_call_repository = CastingCallRepository(db)
    project_repository = ProjectRepository(db)
    role_repository = RoleRepository(db)

    if casting_state == "Publicado":
        raise HTTPException(status_code=400, 
                            detail="The casting must be paused to be updated.")
    if casting_state == "Finalizado":
        raise HTTPException(status_code=400, 
                            detail="The casting has finished and cant be edited.")

    if not added_casting_call_photos: added_casting_call_photos = []
    if not deleted_casting_call_photos or deleted_casting_call_photos == '""': #Puede llegar a venir con un str que es ""
        deleted_casting_call_photos = []
    else:
        deleted_casting_call_photos = deleted_casting_call_photos[1:-1].split(',')

    #Validamos que haya enviado entidades que existen en la bdd
    if not project_repository.get_project_by_id(project_id):
        raise HTTPException(status_code=404, 
                            detail=f"Project with id {project_id} not found.")

    #Validacion y armado de lista de roles
    roles_list = []
    for role_data in casting_roles:
        role = json.loads(role_data)
        
        #Validacion de campos requeridos por cada rol
        if not role.get('role_id'):
            raise HTTPException(status_code=400, 
                                detail="role_id is required for each role.")

        #Validacion de ids existentes en la bdd
        if not role_repository.get_role_by_id(role["role_id"]):
            raise HTTPException(status_code=404, 
                                detail=f"Role with id {role['role_id']} not found.")

        roles_list.append(role)

    filepath = settings.casting_call_photos_path
    #Se eliminan las fotos correspondientes y se agregan las nuevas, si hay
    #TODO: si falla update de casting call se deben reestablecer las fotos eliminadas
    deleted_photos_names = []
    for photo_url in deleted_casting_call_photos:
        photo_name = photo_url.split('/')[-1] #extraemos de la url solo el nombre con su
        if not await storage_manager.delete_file(filepath, photo_name):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Invalid file {photo_name} for deleting.")
        deleted_photos_names.append(photo_name)

    #TODO: si falla update de casting call se deben eliminar las fotos agregadas
    new_photos_names = await store_casting_photos(added_casting_call_photos)

    #Almacenamiento del casting en la bdd junto con sus roles
    updated_casting_call = {"title": title, 
                        "description": description, 
                        "project_id": project_id,
                        "remuneration_type": remuneration_type}

    # Se le manda los nuevos datos del casting junto a los roles expuestos actualizados
    # y las fotos que se eliminaron y las que se agregaron
    casting_call_updated, message = casting_call_repository.update_casting_call_with_exposed_roles(casting_id,
                                                                                          updated_casting_call, 
                                                                                          roles_list,
                                                                                          deleted_photos_names,
                                                                                          new_photos_names.split(','))
    if not casting_call_updated:
        raise HTTPException(status_code=404, detail=message)

    return {'success': True, 'status_code': status.HTTP_200_OK,
            'casting_call_title': title, 'casting_call_id': casting_id }

@router.delete("/{casting_call_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_casting_call(casting_call_id: int, db: Session = Depends(get_db)):
    casting_call_repository = CastingCallRepository(db)

    casting_call = casting_call_repository.get_casting_call_by_id(casting_call_id)

    if not casting_call:
        raise HTTPException(status_code=404, 
                            detail=f"Casting call with id {casting_call_id} not found")
    
    if casting_call.state == "Publicado":
        raise HTTPException(status_code=400, 
                            detail="The casting call cant be deleted cause its published.")
    
    if casting_call.state == "Pausado":
            raise HTTPException(status_code=400, 
                        detail="The casting call cant be deleted cause its paused. Finish it first.")
    
    deleted_casting_call = casting_call_repository.delete_casting_call(casting_call_id)
    
    if not deleted_casting_call:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An error occurred while deleting the casting call") 
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/with-postulations/{casting_call_id}")
def get_casting_call_with_postulations(casting_call_id: int, 
    db: Session = Depends(get_db)) -> CastingCallResponse:

    casting_call_repository = CastingCallRepository(db)
    casting_call_info = casting_call_repository.get_casting_call_by_id_with_postulations(casting_call_id)

    if not casting_call_info:
        raise HTTPException(status_code=404, detail=f"Casting call with id {casting_call_id} not found.")
    
    add_path_to_photo(casting_call_info)
    
    return casting_call_info

    