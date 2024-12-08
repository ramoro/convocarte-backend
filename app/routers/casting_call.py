from typing import List
from fastapi import HTTPException, Depends, APIRouter, Form
from database import get_db
from starlette import status
from sqlalchemy.orm import Session
import oauth2
import models
from schemas.casting_call import CastingCallPreviewResponse, CastingCallPublication, PublishedCastingCallResponse, CastingCallChangeState
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
    tags=["CastingCalls"]
)

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
    if not project_repository.get_project_by_id(project_id):
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found.")

    #Validacion y armado de lista de roles
    roles_list = []
    for role_data in casting_roles:
        role = json.loads(role_data)
        
        #Validacion de campos requeridos por cada rol
        if not role.get('role_id'):
            raise HTTPException(status_code=400, detail="role_id is required for each role.")
    
        if not role.get('form_template_id'):
            raise HTTPException(status_code=400, detail="Form template is required for each role. Every role needs the field form_template.")
        
        #Validacion de ids existentes en la bdd
        if not role_repository.get_role_by_id(role["role_id"]):
            raise HTTPException(status_code=404, detail=f"Role with id {role['role_id']} not found.")
        if not form_template_repository.get_form_template_by_id(role["form_template_id"]):
            raise HTTPException(status_code=404, detail=f"Form template with id {role['form_template_id']} not found.")
        
        roles_list.append(role)

    #Almacenamiento de fotos y armado de string con nombres generados en hexa para las fotos
    photos_names = ""
    for photo_file in casting_call_photos:
        filepath = settings.casting_call_photos_path

        filename = photo_file.filename
        extension = filename.split(".")[-1].lower()

        if extension not in ["png", "jpg", "jpeg"]:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Photo with not allowed file extension.")
        
        #TODO: eliminar fotos almacenadas si falla add_new_casting_call del repository
        name_to_store, file_url = await storage_manager.store_file(extension, filepath, photo_file, True, 600, 650)
        
        photos_names += name_to_store + ","
    photos_names = photos_names[:-1] #Elimino la coma del final

    #Almacenamiento del casting en la bdd junto con sus roles
    new_casting_call = {"title": title, 
                        "description": description, 
                        "project_id": project_id,
                        "remuneration_type": remuneration_type,
                        "owner_id": current_user.id,
                        "casting_photos": photos_names,
                        "state": "Borrador"} #Arranca en estado Borrador hasta que se publique

    # Se le manda los datos del casting recibidos sumado al id del usuario que lo creo y por otro lado la lista de roles que expondra el casting
    casting_call_created = casting_call_repository.add_new_casting_call(new_casting_call, roles_list)
    if not casting_call_created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the casting call")

    return {'success': True, 'status_code': status.HTTP_201_CREATED,
            'casting_call_title': title, 'casting_call_id': casting_call_created.id }

@router.get("/", response_model=List[CastingCallPreviewResponse])
def get_user_casting_calls(current_user: models.User = Depends(oauth2.get_current_user), 
                        db: Session = Depends(get_db)):
    
    casting_call_repository = CastingCallRepository(db)

    my_casting_calls = casting_call_repository.get_casting_calls_by_user_id(current_user.id)

    for casting_call in my_casting_calls:
        if casting_call.casting_photos:
            #Si es corrida local uso el path local, sino la url para descargar desde google drive
            if "localhost" in settings.backend_url:
                #Se hace un split y se le agrega a cada photo el path donde se ubica localmente
                photos_with_paths = list(map(lambda photo_name : settings.backend_url + settings.casting_call_photos_path[1:] + photo_name, casting_call.casting_photos.split(",")))
            else:
                #Para el caso de google drive, se saca la extension de la foto, quedando solo el nombre, que es el id que tiene en el google drive
                photos_with_paths = list(map(lambda photo_name : CLOUD_STORAGE_URL + photo_name.split('.')[0], casting_call.casting_photos.split(",")))
            
            casting_call.casting_photos = photos_with_paths
        else:
            casting_call.casting_photos = []
    
    return my_casting_calls

@router.patch("/publish/{casting_id}")
def publish_casting_call(casting_id: int, casting_call: CastingCallPublication, 
                         current_user: models.User = Depends(oauth2.get_current_user), 
                         db: Session = Depends(get_db)) -> PublishedCastingCallResponse:
    
    if casting_call.state == "Finalizado":
        raise HTTPException(status_code=400, detail="The casting cannot be published because it has already ended.")

    casting_call_repository = CastingCallRepository(db)

    #Le seteo la fecha de publicacion con la fecha actual
    casting_call_dict = casting_call.model_dump()
    argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
    casting_call_dict['start_date'] = datetime.now(argentina_tz).date()

    #Le seteo el nuevo estado al casting (Publicado)
    casting_call_dict['state'] = "Publicado"

    updated_casting_call = casting_call_repository.update_casting_call(casting_id, casting_call_dict)

    if not updated_casting_call:
        raise HTTPException(status_code=404, detail=f"Casting call with id {casting_id} not found.")

    return updated_casting_call

@router.patch("/pause/{casting_id}")
def stop_casting_call(casting_id: int, casting_call: CastingCallChangeState, 
                         current_user: models.User = Depends(oauth2.get_current_user), 
                         db: Session = Depends(get_db)) -> CastingCallChangeState:
    
    if casting_call.state == "Finalizado":
        raise HTTPException(status_code=400, detail="The casting cannot be stopped because it has already ended.")
    elif casting_call.state == "Borrador":
        raise HTTPException(status_code=400, detail="The casting cannot be paused because it hasn't been published yet.")

    casting_call_repository = CastingCallRepository(db)

    casting_call_dict = casting_call.model_dump()

    #Le seteo el nuevo estado al casting (Pausado)
    casting_call_dict['state'] = "Pausado"

    updated_casting_call = casting_call_repository.update_casting_call(casting_id, casting_call_dict)

    if not updated_casting_call:
        raise HTTPException(status_code=404, detail=f"Casting call with id {casting_id} not found.")

    return updated_casting_call

@router.patch("/finish/{casting_id}")
def stop_casting_call(casting_id: int, casting_call: CastingCallChangeState, 
                         current_user: models.User = Depends(oauth2.get_current_user), 
                         db: Session = Depends(get_db)) -> CastingCallChangeState:
    
    if casting_call.state == "Borrador":
        raise HTTPException(status_code=400, detail="The casting cannot be finished because it hasn't been published yet.")

    casting_call_repository = CastingCallRepository(db)

    casting_call_dict = casting_call.model_dump()

    #Le seteo el nuevo estado al casting (Pausado)
    casting_call_dict['state'] = "Finalizado"

    updated_casting_call = casting_call_repository.update_casting_call(casting_id, casting_call_dict)

    if not updated_casting_call:
        raise HTTPException(status_code=404, detail=f"Casting call with id {casting_id} not found.")

    return updated_casting_call
        