from jose import JWTError, jwt
from datetime import datetime, timedelta
from schemas import user
from fastapi import FastAPI, HTTPException, Depends
from starlette import status
from fastapi.security import OAuth2PasswordBearer
import pytz
from database import get_db
from sqlalchemy.orm import Session
import models
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login') #va nombre del path para logearse

#SECRET_KEY
#Algorithm
#Expiration time - how long the user can be logged

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    """Recibe un diccionario con la data necesaria para crear el token y lo crea con jwt
    a partir de cierta secret key y cierto algoritmo. Devuelve el token de acceso."""
    to_encode = data.copy()

    expire = datetime.now(pytz.utc)+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) #Agregamos propiedad extra de tiempo de expiracion
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    """Recibe un token y una excepcion de credenciales. Valida que el token recibido
    sea valido, sino levanta la excepcion de credencial. Devuelve un scema del tipo TokenData."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) 

        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        
        token_data = user.TokenData(id=id) #-> Se valida antes, pero sirve en caso de que vengan mas cosas en el payload, valida tipos de datos
    except JWTError:
        raise credentials_exception
    
    return token_data
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), account_verification: bool = False):
    """Recibe un token, una conexion a la base de datos y un booleano que indica si se esta haciendo la verificacion de cuenta
    o no. Revisa que el token sea valido y obtiene el usuario correspondiente. Devuelve el usuario obtenido.
    Lanza una excepcion de credencial en caso de que el usuario no este verificado y account_verifitacion sea false."""
    #Esta funcion servira como dependencia para agregar a cada endpoint donde quiero que se valide el token
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    
    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    #Unicamente no se valida que la cuenta esta verificada cuando se corre el endpoint para verificar la cuenta
    if not account_verification and not user.is_verified:
        raise credentials_exception

    return user