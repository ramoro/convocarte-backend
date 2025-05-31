import json
from typing import List
from fastapi import Form, HTTPException, Depends, APIRouter
from database import get_db
from starlette import status
from sqlalchemy.orm import Session
import oauth2
import models
from fastapi import File, UploadFile
from routers.user import get_complete_url_for_profile_picture
from repository.message import MessageRepository
from repository.user import UserRepository
from repository.casting_postulation import CastingPostulationRepository
from config import settings
from schemas.message import Message, UpdatedMessage
from storage_managers.local_storage_manager import LocalStorageManager
from storage_managers.cloud_storage_manager import CloudStorageManager, CLOUD_STORAGE_DOWNLOAD_URL

router = APIRouter(
    prefix="/messages", 
    tags=["Messages"],
    dependencies=[Depends(oauth2.get_current_user)]
)

# Defino el almacenamiento segun si es corrida local o no (si no es local los archivos se almacenan en Google Drive)
if "localhost" in settings.backend_url:
    storage_manager = LocalStorageManager()
else:
    storage_manager = CloudStorageManager() 

def add_complete_url_to_message_files(message_files):
    """Recibe el json con los datos de cada archivo perteneciente al mensaje"""
    print(f"message_files: {message_files}")
    files_dict = json.loads(message_files)

    result = {}
    #Se agrega path completo para ser descargados a cada archivo del mensaje
    for file_code, file_name in files_dict.items():
        if "localhost" in settings.backend_url:
            result[settings.backend_url + settings.message_files_path[1:] + file_code] = file_name #Con el [1:] se saca el "."
        else:
            #Sacamos la extension para quedarnos solo con el id del archivo
            result[CLOUD_STORAGE_DOWNLOAD_URL + file_code.split('.')[0] ] = file_name

    return json.dumps(result)

async def store_message_files(new_message_files):
    """Recibe una lista de files que representan archivos adjuntos al mensaje. 
    Recorre esta lista y almacena cada archivo en la carpeta correspondiente.
    Devuelve un diccionario con los nombres generados para almacenar las fotos como claves y 
    los nombres originales como valor."""
    #Diccionario que tendra el nombre nuevo del archivo como clave y el nombre viejo como valor
    new_files_names = {}
    filepath = settings.message_files_path
    for file in new_message_files:

        filename = file.filename
        extension = filename.split(".")[-1].lower()
        
        name_to_store, file_url = await storage_manager.store_file(extension, 
                                                                   filepath, 
                                                                   file, 
                                                                   False)
        
        new_files_names[name_to_store] = filename
        
    return new_files_names

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_message(content: str = Form(...), 
                         receiver_id: int = Form(...), 
                         postulation_id: int = Form(...), 
                         message_files: List[UploadFile] = File(None),
                         previous_message_id: int = Form(None),
                         current_user: models.User = Depends(oauth2.get_current_user), 
                         db: Session = Depends(get_db)):
    
    message_repository = MessageRepository(db)
    casting_postulation_repository = CastingPostulationRepository(db)
    user_repository = UserRepository(db)

    if not message_files: message_files = [] 

    if not casting_postulation_repository.get_casting_postulation_by_id(postulation_id):
        raise HTTPException(status_code=404, 
                            detail=f"Postulation with id {postulation_id} not found.")

    if not user_repository.get_user_by_id(receiver_id):
        raise HTTPException(status_code=404, 
                            detail=f"User with id {receiver_id} not found.")

    #Almacenamiento de archivos adjuntos al mensaje
    #TODO: Si luego falla creacion de mensaje hay q eliminar archivos creados
    files_names = await store_message_files(message_files)
    new_message = {"content": content, 
                    "sender_id": current_user.id,
                    "receiver_id": receiver_id, 
                    "postulation_id": postulation_id,
                    "files": json.dumps(files_names, ensure_ascii=False),
                    "state": "Enviado - Sin Leer"} 

    if previous_message_id:
        new_message["previous_message_id"] = previous_message_id

    message_created = message_repository.add_new_message(new_message)

    if not message_created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="An error occurred while creating the message")
    
    #Agrega path completo para devolverlos al front luego de la creacion y poder visualizarlos desde alli
    files_with_complete_url = add_complete_url_to_message_files(message_created.files)
    
    return {'success': True, 'status_code': status.HTTP_201_CREATED,
            'id': message_created.id, 'created_at': message_created.created_at, 
            'files': files_with_complete_url}

@router.get("/{postulation_id}", response_model=List[Message])
def get_postulation_messages(postulation_id: int, 
                        db: Session = Depends(get_db)):
    
    message_repository = MessageRepository(db)
    casting_postulation_repository = CastingPostulationRepository(db)
    casting_postulation = casting_postulation_repository.get_casting_postulation_by_id(postulation_id)

    if not casting_postulation:
        raise HTTPException(status_code=404, detail=f"Casting postulation with id {postulation_id} not found.")

    postulation_messages = message_repository.get_messages_by_postulation_id(postulation_id)

    #Transformo resultado de tuplas a lista de diccionaris, y agrego path completo a
    #la foto de perfil del emisor
    postulation_messages = [
            {
                "id": msg.id,
                "content": msg.content,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "postulation_id": msg.postulation_id,
                "files": msg.files,
                "state": msg.state,
                "created_at": msg.created_at,
                "previous_message_id": msg.previous_message_id,
                "sender_fullname": fullname,
                "sender_profile_picture": get_complete_url_for_profile_picture(profile_picture)
            }
            for msg, fullname, profile_picture in postulation_messages
        ]

    for message in postulation_messages:
        if message["files"]:
            message["files"] = add_complete_url_to_message_files(message["files"])
    
    return postulation_messages

@router.patch("/{message_id}")
def update_message_partially(message_id: int, updated_message: UpdatedMessage, 
                        db: Session = Depends(get_db)):
    message_repository = MessageRepository(db)
    message = message_repository.get_message_by_id(message_id)

    if not message:
        raise HTTPException(status_code=404, detail=f"Message with id {message_id} not found.")
    
    message_repository.update_message_partially(updated_message.model_dump(exclude_unset=True), message_id)

    return {"success": True, "status_code": status.HTTP_200_OK, "message": "Message updated successfully."}

@router.post("/many-users", status_code=status.HTTP_201_CREATED)
async def create_message_for_many_users(content: str = Form(...), 
                         postulations: str = Form(...), 
                         message_files: List[UploadFile] = File(None),
                         placeholder_to_replace: str = Form(None),
                         current_user: models.User = Depends(oauth2.get_current_user), 
                         db: Session = Depends(get_db)):
    
    message_repository = MessageRepository(db)

    if not message_files: message_files = [] 

    #Almacenamiento de archivos adjuntos al mensaje
    #TODO: Si luego falla creacion de mensaje hay q eliminar archivos creados
    files_names = await store_message_files(message_files)


    message_created, error = message_repository.add_new_message_for_many_users(content,
                                                                        json.dumps(files_names, ensure_ascii=False),
                                                                        postulations,
                                                                        placeholder_to_replace,
                                                                        current_user.id
                                                                        )

    if not message_created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"An error occurred while creating the message for many users: {error}")
       
    return {'success': True, 'status_code': status.HTTP_201_CREATED}