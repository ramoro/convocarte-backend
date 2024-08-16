from fastapi import HTTPException, Depends, APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repository.user import UserRepository
from starlette import status
from starlette.responses import Response
from typing import List, Optional
from sqlalchemy.orm import Session
import models
from schemas.user import CreateUser, UpdateUser, UserResponse, ForgetPasswordRequest, ResetForgetPassword
from database import get_db
import utils
import oauth2
import mailer

router = APIRouter(
    prefix="/users", #Indica que cada endpoint de este router va a comenzar con /users. Evita tener que pegarlo en todos lados
    tags=["Users"] #Crea grupo para endpoints de users en la doc de FastApi
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(request: Request, user: CreateUser, db: Session = Depends(get_db)):
    user_repository = UserRepository()
    existing_user = user_repository.get_user_by_email(user.email)

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The email is already used.")

    if not utils.is_valid_password(user.password, user.password_confirmation):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password: passwords must match and must be at least 8 characters long, contain a number, an uppercase letter, a lowercase letter, and a special character (#,-,_,$,%,&,*).")
    
    #hash the password -> user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
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
def email_verification(token: str):
    user_repository = UserRepository()
    try:
        current_user = oauth2.get_current_user(token, user_repository, True)
    except Exception as e:
        #Si el token es invalido, ya sea porque esta falseado o caduco, el usuario no se verifica
        return RedirectResponse(url=f"http://localhost:8080/verified-account/None/None")
    
    if not current_user.is_verified:
        user_repository.update_user(current_user.id, {"is_verified": True})

    return RedirectResponse(url=f"http://localhost:8080/verified-account/{current_user.id}/{token}")

@router.post('/password-recovering')
def password_recovering(request: Request, pass_req: ForgetPasswordRequest):

    user_repository = UserRepository()  
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
def reset_password(rfp: ResetForgetPassword):
    user_repository = UserRepository()
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

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = 
                Depends(oauth2.get_current_user)):

    #cursor.execute("""SELECT * FROM users where users.id = %s""", (str(user_id)))
    #user = cursor.fetchone() 
    user = db.query(models.User).filter(models.User.id == user_id).first() #Se usa first y no all porque se sabe q por id es unico, sino seguiria buscando y gastaria mas tiempo
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with {user_id} not found")
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
    

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_user: UpdateUser, db: Session = Depends(get_db), current_user: models.User = 
                Depends(oauth2.get_current_user)):
    #cursor.execute("""UPDATE users
    #               set username = %s,
    #               fullname = %s,
    #               email = %s,
    #               password = %s
    #               where id = %s
    #               returning *""", (user.username, user.fullname, user.email, user.password, user_id))
    #updated_user = cursor.fetchone()
    #conn.commit()

    user_query = db.query(models.User).filter(models.User.id == user_id)

    user = user_query.first()
    
    if user == None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    user_query.update(updated_user.model_dump(), synchronize_session=False)
    db.commit()

    return user_query.first()