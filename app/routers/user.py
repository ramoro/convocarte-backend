from fastapi import HTTPException, Depends, APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repository.user import UserRepository
from repository.academic_experience import AcademicExperienceRepository
from repository.work_experience import WorkExperienceRepository
from schemas.user import CreateUser, UpdateUser, UserResponse, ForgetPasswordRequest, ResetForgetPassword ,UserFullResponse
from schemas.academic_experience import AcademicExperienceBase, AcademicExperienceUpdate, AcademicExperienceResponse
from schemas.work_experience import WorkExperienceBase, WorkExperienceResponse, WorkExperienceUpdate
from database import get_db
from starlette import status
from starlette.responses import Response
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image
from config import settings
import models
import utils
import oauth2
import mailer
import io
import base64

router = APIRouter(
    prefix="/users", #Indica que cada endpoint de este router va a comenzar con /users. Evita tener que pegarlo en todos lados
    tags=["Users"] #Crea grupo para endpoints de users en la doc de FastApi
)

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
    email_verification_link = f"http://localhost/users/verification/?token={access_token}"
    
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
        return RedirectResponse(url=f"http://localhost:8080/verified-account/None/None")
    
    if not current_user.is_verified:
        user_repository.update_user(current_user.id, {"is_verified": True})

    return RedirectResponse(url=f"http://localhost:8080/verified-account/{current_user.id}/{token}")

@router.post('/password-recovering')
def password_recovering(request: Request, pass_req: ForgetPasswordRequest, db: Session = Depends(get_db)):

    user_repository = UserRepository(db)  
    existing_user = user_repository.get_user_by_email(pass_req.email)
    
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email address.")
    
    secret_token = oauth2.create_access_token(data = {"user_id": existing_user.id})
    reset_password_link = f"http://localhost:8080/reset-password/{secret_token}"

    context = {
        "request": request,
        "reset_password_link": reset_password_link
    }
    #Se envia email de recuperacion de contraseña
    mailer.send_email(existing_user.email, "ConvocArte - Recuperación de contraseña", context, "password-recovering.html")

    return {"message": "Email has been sent", "success": True,
        "status_code": status.HTTP_200_OK}

@router.post("/reset-password")
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


@router.post("/upload-profile-picture", )
async def create_profile_picture(file: UploadFile = File(...),
                                current_user: models.User = Depends(oauth2.get_current_user),
                                db: Session = Depends(get_db)):
    filepath = settings.profile_pictures_path
    filename = file.filename
    extension = filename.split(".")[-1].lower()

    if extension not in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File extension not allowed.")
    
    token_name = await utils.store_file(extension, filepath, file, current_user.profile_picture)
    generated_name = filepath + token_name
    
    img = Image.open(generated_name)
    #img = img.resize(size=(200, 200))
    img.save(generated_name)

    # Convertir la imagen a base64 para enviar al frontend. Pillow no acepta JPG
    buffered = io.BytesIO()
    img.save(buffered, format='JPEG' if extension == 'jpg' else extension.upper())
    img_str = base64.b64encode(buffered.getvalue()).decode()

    user_repository = UserRepository(db)
    user_repository.update_user(current_user.id, {"profile_picture": token_name})

    file_url="http://localhost" + generated_name[1:]
    return {'success': True, 'status_code': status.HTTP_200_OK,
            'filename': file_url, 'image': img_str}

@router.post("/upload-cv", )
async def update_cv(file: UploadFile = File(...),
                                current_user: models.User = Depends(oauth2.get_current_user),
                                db: Session = Depends(get_db)):
    filepath = settings.cvs_path
    filename = file.filename
    extension = filename.split(".")[-1].lower()

    if extension not in ["pdf"]:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File extension not allowed.")
    
    token_name = await utils.store_file(extension, filepath, file, current_user.cv)
    generated_name = filepath + token_name
    
    user_repository = UserRepository(db)
    user_repository.update_user(current_user.id, {"cv": token_name})

    file_url="http://localhost" + generated_name[1:]
    return {'success': True, 'status_code': status.HTTP_200_OK,
            'filename': file_url}

@router.post("/add-academic-experience", response_model=AcademicExperienceResponse)
async def add_academic_experience(new_academic_experience: AcademicExperienceBase, 
                                  current_user: models.User = Depends(oauth2.get_current_user),
                                  db: Session = Depends(get_db)):
    academic_exp_repository = AcademicExperienceRepository(db)
    dict_academic_exp = new_academic_experience.model_dump()
    dict_academic_exp['user_id'] = current_user.id
    new_academic_exp = academic_exp_repository.add_new_academic_experience(dict_academic_exp)

    return new_academic_exp

@router.get("/my-academic-experiences", response_model=List[AcademicExperienceResponse])
async def list_academic_experiences(current_user: models.User = Depends(oauth2.get_current_user),
                                    db: Session = Depends(get_db)):
    academic_exp_repository = AcademicExperienceRepository(db)
    
    my_academic_experiences = academic_exp_repository.get_academic_experiences_by_user_id(current_user.id)

    return my_academic_experiences

@router.delete("/delete-academic-experience/{academic_exp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_academic_experience(academic_exp_id: int, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    academic_exp_repository = AcademicExperienceRepository(db)

    deleted = academic_exp_repository.delete_academic_experience(academic_exp_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Academic experience {academic_exp_id} not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/update-academic-experience/{academic_exp_id}", response_model=AcademicExperienceBase)
def update_academic_experience(academic_exp_id: int, updated_academic_exp: AcademicExperienceUpdate, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    academic_exp_repository = AcademicExperienceRepository(db)
    updated_exp = academic_exp_repository.update_academic_experience(academic_exp_id, updated_academic_exp.model_dump())

    if not updated_exp:
        raise HTTPException(status_code=404, detail=f"Academic experience {academic_exp_id} not found")

    return updated_exp

@router.post("/add-work-experience", response_model=WorkExperienceResponse)
async def add_work_experience(new_work_experience: WorkExperienceBase, 
                                  current_user: models.User = Depends(oauth2.get_current_user),
                                  db: Session = Depends(get_db)):
    work_exp_repository = WorkExperienceRepository(db)
    dict_work_exp = new_work_experience.model_dump()
    dict_work_exp['user_id'] = current_user.id
    new_work_exp = work_exp_repository.add_new_work_experience(dict_work_exp)

    return new_work_exp

@router.get("/my-work-experiences", response_model=List[WorkExperienceResponse])
async def list_work_experiences(current_user: models.User = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    work_exp_repository = WorkExperienceRepository(db)
    
    my_work_experiences = work_exp_repository.get_work_experiences_by_user_id(current_user.id)

    return my_work_experiences

@router.delete("/delete-work-experience/{work_exp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_experience(work_exp_id: int, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    work_exp_repository = WorkExperienceRepository(db)

    deleted = work_exp_repository.delete_work_experience(work_exp_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Work experience {work_exp_id} not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/update-work-experience/{work_exp_id}", response_model=WorkExperienceBase)
def update_work_experience(work_exp_id: int, updated_work_exp: WorkExperienceUpdate, current_user: models.User = 
                Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    work_exp_repository = WorkExperienceRepository(db)
    updated_exp = work_exp_repository.update_work_experience(work_exp_id, updated_work_exp.model_dump())

    if not updated_exp:
        raise HTTPException(status_code=404, detail=f"Work experience {work_exp_id} not found")

    return updated_exp

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
        user.cv = "http://localhost" + settings.cvs_path[1:] + user.cv

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