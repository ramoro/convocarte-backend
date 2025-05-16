from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from starlette import status
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import UserLogin
import models
import utils
import oauth2
from routers.user import get_complete_url_for_profile_picture

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=UserLogin)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #Con oauth ahora espera el email y la pass en form-data
    user = db.query(models.User).filter(
        (models.User.email == user_credentials.username)
        ).first()
    
    if not user or not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Invalid Credentials")
    
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Unverified Account")
    
    access_token = oauth2.create_access_token(data = {"user_id": user.id})

    profile_picture_path = ""
    if user.profile_picture:
        profile_picture_path = get_complete_url_for_profile_picture(user.profile_picture)

    return {"id": user.id, "email": user.email, "fullname": user.fullname, 
            "profile_picture": profile_picture_path, "token": access_token, "token_type": "bearer"}

