from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import Response
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import UserLogin
import models
import utils
import oauth2
from config import settings
from storage_managers.cloud_storage_manager import CLOUD_STORAGE_URL 

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=UserLogin)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #Con oauth ahora espera el email y la pass en form-data
    user = db.query(models.User).filter(
        (models.User.email == user_credentials.username)
        ).first()
    
    if not user or not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unverified Account")
    
    access_token = oauth2.create_access_token(data = {"user_id": user.id})

    profile_picture_path = ""
    if user.profile_picture:
        #Si es corrida local uso el path local, sino el almacenamiento en google drive
        if "localhost" in settings.backend_url:
            profile_picture_path = settings.backend_url + settings.profile_pictures_path[1:] + user.profile_picture
        else:
            profile_picture_path = CLOUD_STORAGE_URL + user.profile_picture.split('.')[0] #removemos la extension ya que solo necesitamos el id de la foto en el google drive
            print("profile picture path", profile_picture_path)

    return {"id": user.id, "email": user.email, "fullname": user.fullname, "profile_picture": profile_picture_path, "token": access_token, "token_type": "bearer"}

