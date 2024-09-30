from passlib.context import CryptContext
import re
import secrets
import os

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
    return pwd_context.verify(plain_password, hashed_password) #Usar la plain password para hashearla y compararla con la password hasheada obtenida de la bdd

async def store_file(extension, filepath, new_file, existing_file):
    """Recibe la extension de un archivo, el path donde deberia ser almacenado, el contenido del archivo
    a almacenar y el archivo ya existente a ser reemplazado. Genera un nombre en hexadecimal para el archivo
    nuevo y lo almacena en el path indicado reemplazando el ya existente. Devuelve el nombre en hexadecimal generado."""
    #Genero numero random para el token, que seria le nombre de la imagen, para que no se pisen
    token_name = secrets.token_hex(10) + "." + extension
    generated_name = filepath + token_name
    file_content = await new_file.read()

    # Eliminar la imagen de perfil anterior si existe
    current_profile_picture = existing_file

    if current_profile_picture:
        old_image_path = filepath + existing_file
        if os.path.exists(old_image_path):
            os.remove(old_image_path)

    with open(generated_name, "wb") as file:
        file.write(file_content)

    return token_name