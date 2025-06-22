import json
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile
from requests import Session
import oauth2
import models
from database import get_db
from storage_managers.local_storage_manager import LocalStorageManager
from storage_managers.cloud_storage_manager import CloudStorageManager, CLOUD_STORAGE_URL
from config import settings
from starlette import status
from repository.open_role import OpenRoleRepository
from repository.casting_postulation import CastingPostulationRepository
from repository.form import FormRepository
from schemas.casting_postulation import CastingPostulationResponse


if "localhost" in settings.backend_url:
    storage_manager = LocalStorageManager()
else:
    storage_manager = CloudStorageManager() 


router = APIRouter(
    prefix="/casting-postulations", 
    tags=["CastingPostulations"],
    dependencies=[Depends(oauth2.get_current_user)]
)

PHOTO_TYPES_NAMES=["Foto Plano Pecho", "Foto Plano General", "Foto un Perfil", "Foto Adicional 1", "Foto Adicional 2"]

#El nombre del cv y las fotos para accederlos desde el front
#seran almacenadados en postulation_data, donde la clave sera
#el nombre con el que venga el archivo
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_casting_postulation(form_id: int = Form(...),
                        postulation_data: str = Form(...),
                        postulation_cv_file: UploadFile = File(None), #es opcional el CV
                        postulation_photos: List[UploadFile] = File(None), 
                        current_user: models.User = Depends(oauth2.get_current_user), 
                        db: Session = Depends(get_db)):

    try:
        postulation_dict = json.loads(postulation_data)  # Convertir a diccionario
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in postulation_data")

    open_role_repository = OpenRoleRepository(db)
    form_repository = FormRepository(db)

    #Validacion de existencia del form
    form = form_repository.get_form_by_id(form_id)

    if not form:
        raise HTTPException(status_code=404, 
                    detail=f"Form with id {form_id} not found.")

    open_role_data = open_role_repository.get_open_role_with_casting_by_form_id(form_id)

    #Validacion para caso en que rol este lleno
    if open_role_data['has_limited_spots'] and open_role_data['occupied_spots'] >= open_role_data['spots_amount']:
        raise HTTPException(status_code=400, 
                            detail="The role open for this casting call is full. No more postulations are allowed.")
    
    #Validacion para caso en el que el usuario ya se ha postulado para ese rol
    casting_postulation_repository = CastingPostulationRepository(db)
    casting_postulation = casting_postulation_repository.get_casting_postulation_by_user_and_open_role(current_user.id, 
                                                                                    open_role_data['open_role_id'])

    if casting_postulation:
        raise HTTPException(status_code=400, 
                            detail="The user has already postulated for this role.")
    
    #Validacion para el caso en el que el casting haya finalizado o este pausado
    if open_role_data["casting_call_state"] == "Finalizado":
        raise HTTPException(status_code=400, 
                            detail="The casting call for this role has already finished.")
    elif open_role_data["casting_call_state"] == "Pausado":
        raise HTTPException(status_code=400, 
                            detail="The casting call for this role is paused.")
    
    filepath = settings.postulation_files_path

    #Almacenamiento del Curriculum si es que viene con cv
    #Si no viene con cv pero viene con el campo Curriculum lleno
    #Significa que viene con la url del cv que tiene por defecto el usuario
    #Se genera copia de ese file y se lo traslada a la carpeta de archivos de postulacion
    if postulation_cv_file:
        filename = postulation_cv_file.filename
        filename_without_extension = filename.split(".")[0]
        extension = filename.split(".")[-1].lower()

        if extension not in ["pdf"]:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="CV extension not allowed.")

        #Corregir el file_url que se genera para el cv, ya que tiene que tener el path de download
        name_to_store_in_db, cv_file_url = await storage_manager.store_file(extension, filepath, 
                                                                        postulation_cv_file, False)
        postulation_dict[filename_without_extension] = name_to_store_in_db
    
    elif "Curriculum" in postulation_dict and postulation_dict["Curriculum"]:
         filename_to_copy = postulation_dict["Curriculum"].split('/')[-1]
         #Para el caso en que se este almacenando los archivos con google Drive
         #y viene el archivo con el id e info extra para poder descargarlo
         #desde el drive
         if "download" in filename_to_copy:
             filename_to_copy = filename_to_copy.split('=')[-1]
         new_name = storage_manager.copy_file(settings.cvs_path, filename_to_copy, 
                                                 settings.postulation_files_path)
         postulation_dict["Curriculum"] = new_name
 
    #Por cada foto que este en la postulation_data
    #significa que viene solo con su url, es decir, que venia
    #ya sobrecargada del perfil del usuario. Simplemente hay que copiarla
    for photo_type in PHOTO_TYPES_NAMES:
        if photo_type in postulation_dict and postulation_dict[photo_type]:
            filename_to_copy = postulation_dict[photo_type].split('/')[-1]
            new_name = storage_manager.copy_file(settings.gallery_shots_path, filename_to_copy, 
                                                    settings.postulation_files_path)
            postulation_dict[photo_type] = new_name
            
    #Almacenamiento de fotos de postulacion si es que hay
    if not postulation_photos: 
        postulation_photos = []
    
    for photo_file in postulation_photos:

        filename = photo_file.filename
        extension = filename.split(".")[-1].lower()
        filename_without_extension = filename.split(".")[0]

        if extension not in ["png", "jpg", "jpeg"]:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Photo {filename} with not allowed file extension.")
        
        name_to_store, file_url = await storage_manager.store_file(extension, 
                                                                filepath, 
                                                                photo_file, 
                                                                True, 600, 650)
        postulation_dict[filename_without_extension] = name_to_store

    #Crea postulacion para el casting
    new_casting_postulation = {"casting_call_id": open_role_data['casting_call_id'],
                            "open_role_id": open_role_data['open_role_id'],
                            "owner_id": current_user.id,
                            "state": "Pendiente"
                            }
    
    #TODO: si falla el almacenado de la postulacion se deben eliminar los archivos almacenados
    casting_postulation_created = casting_postulation_repository.add_new_casting_postulation(new_casting_postulation,
                                                                                                postulation_dict)

    #Aumentamos en uno los cupos ocupados para el rol expuesto en caso de que tenga cupos limitados
    if open_role_data['has_limited_spots']:
        open_role_repository.update_occupied_spots(open_role_data["open_role_id"], 
                                                    open_role_data['occupied_spots'] + 1)
    
    return {'success': True, 'status_code': status.HTTP_201_CREATED, 'id': casting_postulation_created.id}

@router.get("/{postulation_id}")
def get_casting_postulation(postulation_id: int, 
                        db: Session = Depends(get_db)) -> CastingPostulationResponse:
    
    casting_postulation_repository = CastingPostulationRepository(db)
    casting_postulation = casting_postulation_repository.get_casting_postulation_by_id(postulation_id)

    if not casting_postulation:
        raise HTTPException(status_code=404, detail=f"Casting postulation with id {postulation_id} not found.")
    
    #TODO:Agregar path a fotos y CV en postulation_data devuelta    
    return casting_postulation