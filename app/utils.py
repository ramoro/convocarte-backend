from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def is_valid_password(password:str, password_confirmation: str):
    """Recibe dos password, valida que sean iguales y que cumplan con los requisitos de tener al menos 8
    caracteres, un numero, una mayuscula, una minuscula y un caracter especial. Devuelve true en caso de
    cumplir con los requisitos, false en caso contrario."""
    return password == password_confirmation and \
    re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#,\-_$%&*]).{8,}$', password)

def hash(password: str):
    """Recibe una contraseña y devuelve la misma pero hasheada."""
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    """Recibe una contraseña y una contraseña hasheada. Devuelve true en caso de que sean las mismas.
    False en caso contrario."""
    return pwd_context.verify(plain_password, hashed_password) #Usara la plain password para hashearla y compararla con la password hasheada obtenida de la bdd