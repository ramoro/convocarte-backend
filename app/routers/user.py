from fastapi import HTTPException, Depends, APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repository.user import UserRepository
from schemas.user import CreateUser, UpdateUser, UserResponse, ForgetPasswordRequest, ResetForgetPassword ,UserFullResponse, DeleteUserFile
from database import get_db
from starlette import status
from starlette.responses import Response
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
from typing import Optional
from PIL import Image
from config import settings
from storage_managers.local_storage_manager import LocalStorageManager
from storage_managers.cloud_storage_manager import CloudStorageManager
from storage_managers.cloud_storage_manager import CLOUD_STORAGE_DOWNLOAD_URL
from storage_managers.cloud_storage_manager import CLOUD_STORAGE_URL
import models
import utils
import oauth2
import mailer


router = APIRouter(
    prefix="/users", #Indica que cada endpoint de este router va a comenzar con /users. Evita tener que pegarlo en todos lados
    tags=["Users"] #Crea grupo para endpoints de users en la doc de FastApi
)


# Defino el almacenamiento segun si es corrida local o no (si no es local los archivos se almacenan en Google Drive)
if "localhost" in settings.backend_url:
    storage_manager = LocalStorageManager()
else:
    storage_manager = CloudStorageManager() 

# Atributos del modelo Usuario que llevan un string con la direccion de una imagen de la galeria del usuario
# Los atributos son: foto plano pecho, foto de plano general, foto de perfil y dos fotos adicionales
USER_SHOTS_ATTRIBUTES = ["chest_up_shot", "full_body_shot", "profile_shot", "additional_shot_1", "additional_shot_2"]
def add_complete_url_shots(user):
    for attribute in USER_SHOTS_ATTRIBUTES:
        if getattr(user, attribute):
            if "localhost" in settings.backend_url:
                shot_url = settings.backend_url + settings.gallery_shots_path[1:] + getattr(user, attribute)
            else:
                shot_url = CLOUD_STORAGE_URL + getattr(user, attribute).split('.')[0] #Saco la extension, para google drive solo me interesa el id
            setattr(user, attribute, shot_url)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(request: Request, user: CreateUser, db: Session = Depends(get_db)):
    user_repository = UserRepository(db)
    existing_user = user_repository.get_user_by_email(user.email)

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The email is already used.")

    if not utils.is_valid_password(user.password, user.password_confirmation):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password: passwords must match and must be at least 8 characters long, contain a number, an uppercase letter, a lowercase letter, and a special character (#,-,_,$,%,&,*).")
    
    #hash the password -> user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    user.fullname = user.fullname.title() #Pasamos a mayusculas la primera letra
    dict_user = user.model_dump()
    dict_user.pop("password_confirmation")
    new_user = user_repository.add_new_user(dict_user)

    access_token = oauth2.create_access_token(data = {"user_id": new_user.id})
    email_verification_link = settings.backend_url + f"/users/verification/?token={access_token}"
    
    context = {
        "request": request,
        "email_verification_link": email_verification_link
    }

    #Se envia email de verificacion
    mailer.send_email(new_user.email, "ConvocArte - Verificación de cuenta", context, "email-verification.html")
    
    return new_user

@router.get('/verification', response_model=UserResponse)
def email_verification(token: str, db: Session = Depends(get_db)):
    user_repository = UserRepository(db)
    try:
        print(f"Token en verification: {token}")
        current_user = oauth2.get_current_user(token, db, True)
    except Exception as e:
        #Si el token es invalido, ya sea porque esta falseado o caduco, el usuario no se verifica
        return RedirectResponse(url=settings.frontend_url + "/verified-account/None/None")
    
    if not current_user.is_verified:
        user_repository.update_user(current_user.id, {"is_verified": True})

    return RedirectResponse(url=settings.frontend_url + f"/verified-account/{current_user.id}/{token}")

@router.patch('/password-recovering')
def password_recovering(request: Request, pass_req: ForgetPasswordRequest, db: Session = Depends(get_db)):

    user_repository = UserRepository(db)  
    existing_user = user_repository.get_user_by_email(pass_req.email)
    
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email address.")
    
    secret_token = oauth2.create_access_token(data = {"user_id": existing_user.id})
    reset_password_link = settings.frontend_url + f"/reset-password/{secret_token}"

    context = {
        "request": request,
        "reset_password_link": reset_password_link
    }
    #Se envia email de recuperacion de contraseña
    mailer.send_email(existing_user.email, "ConvocArte - Recuperación de contraseña", context, "password-recovering.html")

    return {"message": "Email has been sent", "success": True,
        "status_code": status.HTTP_200_OK}

@router.patch("/reset-password")
def reset_password(rfp: ResetForgetPassword, db: Session = Depends(get_db)):
    user_repository = UserRepository(db)
    token_exception = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid Password Reset Payload or Reset Link Expired")
    info = oauth2.verify_access_token(rfp.secret_token, token_exception)
    
    if info is None:
        raise token_exception
    
    if rfp.new_password != rfp.password_confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords must match.")
    
    hashed_password = utils.hash(rfp.new_password)
    user_repository.update_user(info.id, {"password": hashed_password})

    return {'success': True, 'status_code': status.HTTP_200_OK,
                'message': 'Password Rest Successfull!'}

@router.patch("/upload-image", )
async def create_image(file: UploadFile = File(...),
                            field_name: str = Form(...),
                            old_file_name: Optional[str] = Form(None), 
                            current_user: models.User = Depends(oauth2.get_current_user),
                            db: Session = Depends(get_db)):
    
    #Depende que tipo de foto es, se guarda en diferentes paths
    filepath = ""
    if field_name == 'profile_picture':
        filepath = settings.profile_pictures_path
    elif field_name in USER_SHOTS_ATTRIBUTES:
        filepath = settings.gallery_shots_path

    filename = file.filename
    extension = filename.split(".")[-1].lower()

    if extension not in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File extension not allowed.")

    #En caso de que ya había un archivo antes se recibe su nombre para eliminarlo del back
    if old_file_name != "null":
        if not await storage_manager.delete_file(filepath, old_file_name):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid old file name.")
    
    name_to_store = ""
    #Solo se indica la redimension en el caso de las fotos de la galeria
    if field_name in USER_SHOTS_ATTRIBUTES:
        name_to_store, file_url = await storage_manager.store_file(extension, filepath, file, current_user.profile_picture, True, 600, 650)
    else:
        name_to_store, file_url = await storage_manager.store_file(extension, filepath, file, current_user.profile_picture, False)
        
    # img = Image.open(generated_name)
    # img = img.resize(size=(200, 200))
    # img.save(generated_name)

    # # Convertir la imagen a base64 para enviar al frontend. Pillow no acepta JPG
    # buffered = io.BytesIO()
    # img.save(buffered, format='JPEG' if extension == 'jpg' else extension.upper())
    # img_str = base64.b64encode(buffered.getvalue()).decode()

    user_repository = UserRepository(db)
    user_repository.update_user(current_user.id, {field_name: name_to_store})

    return {'success': True, 'status_code': status.HTTP_200_OK,
            'filename': file_url } #'image': img_str}

@router.patch("/delete-file", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_file(file_data: DeleteUserFile, current_user: models.User = Depends(oauth2.get_current_user),
                                db: Session = Depends(get_db)):
    file_path = ''
    if file_data.field_name == 'cv':
        file_path = settings.cvs_path
    elif file_data.field_name in USER_SHOTS_ATTRIBUTES:
        file_path = settings.gallery_shots_path
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid field name.")
    

    if not await storage_manager.delete_file(file_path, file_data.file_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid file.")

    user_repository = UserRepository(db)
    user_repository.update_user(current_user.id, {file_data.field_name: None})
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch("/upload-cv", )
async def update_cv(file: UploadFile = File(...),
                    old_file_name: Optional[str] = Form(None), 
                    current_user: models.User = Depends(oauth2.get_current_user),
                    db: Session = Depends(get_db)):
    
    filepath = settings.cvs_path

    filename = file.filename
    extension = filename.split(".")[-1].lower()

    if extension not in ["pdf"]:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File extension not allowed.")

    #En caso de que ya había un archivo antes se recibe su nombre para eliminarlo del back
    if old_file_name != "null":
        if not await storage_manager.delete_file(filepath, old_file_name):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid old file name.")
    #Corregir el file_url que se genera para el cv, ya que tiene que tener el path de download
    name_to_store_in_db, file_url = await storage_manager.store_file(extension, filepath, file, current_user.cv, False)
    
    user_repository = UserRepository(db)
    user_repository.update_user(current_user.id, {"cv": name_to_store_in_db})

    return {'success': True, 'status_code': status.HTTP_200_OK,
            'filename': file_url}

@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: models.User = 
                Depends(oauth2.get_current_user)):
    print(current_user.email)
    #cursor.execute("""SELECT * FROM users """)
    #all_users = cursor.fetchall()
    all_users = db.query(models.User).all()
    #return {"data": all_users}
    return all_users


@router.get("/filtered", response_model=List[UserResponse])
def list_filtered_users(db: Session = Depends(get_db), current_user: models.User = 
                Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0,
                search: Optional[str] = ""):
    print(limit) #Limit lo puedo pasar como query parameter
    
    print(current_user.email)
    #cursor.execute("""SELECT * FROM users """)
    #all_users = cursor.fetchall()
    all_users = db.query(models.User).filter(models.User.fullname.contains(search)).limit(limit).offset(skip).all()
    #return {"data": all_users}
    return all_users

@router.get("/{user_id}", response_model=UserFullResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = 
                Depends(oauth2.get_current_user)):
    #cursor.execute("""SELECT * FROM users where users.id = %s""", (str(user_id)))
    #user = cursor.fetchone() 
    user_repository = UserRepository(db)
    user = user_repository.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail=f"User with {user_id} not found")
    
    if user.cv:
        #Si es corrida local uso el path local, sino la url para descargar desde google drive
        if "localhost" in settings.backend_url:
            user.cv = settings.backend_url + settings.cvs_path[1:] + user.cv
        else:
            user.cv = CLOUD_STORAGE_DOWNLOAD_URL + user.cv.split('.')[0] #Sacamos la extension para quedarnos solo con el id del archivo
    
    add_complete_url_shots(user)

    return user

@router.patch("/{user_id}")
def update_user_partially(user_id: int, updated_data: UpdateUser, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    user_respository = UserRepository(db)
    user = user_respository.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail=f"User {user} not found")

    user_respository.update_user(user_id,  updated_data.model_dump(exclude_unset=True)) 
    #exclude_unset es para remover los campos que el usuario no seteo, sino los toma como null y pisa datos
    
    return user
       

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = 
                Depends(oauth2.get_current_user)):

    #cursor.execute("""DELETE FROM users where id = %s returning *""", (str(user_id),))
    #deleted_user = cursor.fetchone()
    #conn.commit()
    user = db.query(models.User).filter(models.User.id == user_id)
    
    if user.first() == None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    

    user.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    

# @router.put("/{user_id}", response_model=UserResponse)
# def update_user(user_id: int, updated_user: UpdateUser, db: Session = Depends(get_db), current_user: models.User = 
#                 Depends(oauth2.get_current_user)):
#     #cursor.execute("""UPDATE users
#     #               set username = %s,
#     #               fullname = %s,
#     #               email = %s,
#     #               password = %s
#     #               where id = %s
#     #               returning *""", (user.username, user.fullname, user.email, user.password, user_id))
#     #updated_user = cursor.fetchone()
#     #conn.commit()

#     user_query = db.query(models.User).filter(models.User.id == user_id)

#     user = user_query.first()
    
#     if user == None:
#         raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
#     user_query.update(updated_user.model_dump(), synchronize_session=False)
#     db.commit()

#     return user_query.first()