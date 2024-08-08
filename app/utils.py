from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def is_valid_password(password:str, password_confirmation: str):
    return password == password_confirmation and \
    re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#,\-_$%&*]).{8,}$', password)

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password) #Usara la plain password para hashearla y compararla con la password hasheada obtenida de la bdd