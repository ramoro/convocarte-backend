from passlib.context import CryptContext
import re
import secrets
import os
from PIL import Image
import io

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

async def resize_image(file_content: bytes, max_width, max_height) -> bytes:
    """Recibe el contenido de un archivo y lo redimensiona usando los parametros de ancho y altura
    recibidos. Devuelve el contenido redimensionado"""

    # Leer el contenido del archivo como una imagen de Pillow
    image = Image.open(io.BytesIO(file_content))

    # Obtener las dimensiones originales de la imagen
    original_width, original_height = image.size

    # Calcular el factor de escala proporcional
    width_ratio = max_width / original_width
    height_ratio = max_height / original_height
    scale_ratio = min(width_ratio, height_ratio)

    # Calcular el nuevo tamaño manteniendo las proporciones
    new_width = int(original_width * scale_ratio)
    new_height = int(original_height * scale_ratio)

    # Redimensionar la imagen
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # Guardar la imagen redimensionada en un buffer de bytes
    output_buffer = io.BytesIO()
    resized_image.save(output_buffer, format=image.format)
    resized_content = output_buffer.getvalue()

    return resized_content

async def store_file(extension, filepath, new_file, existing_file, resize, max_width_resize=0, max_height_resize=0):
    """Recibe la extension de un archivo, el path donde deberia ser almacenado, el contenido del archivo
    a almacenar, el archivo ya existente a ser reemplazado y un booleano que indica si la imagen debe ser redimensionada
    al almacenarse, junto con los valores de redimension. Genera un nombre en hexadecimal para el archivo
    nuevo y lo almacena en el path indicado reemplazando el ya existente. Devuelve el nombre en hexadecimal generado."""
    #Genero numero random para el token, que seria le nombre de la imagen, para que no se pisen
    token_name = secrets.token_hex(10) + "." + extension
    generated_name = filepath + token_name
    file_content = await new_file.read()

    #Hay imagenes como las de la galeria que se redimensionan porque pueden llegar a pesar mucho sino
    if resize:
        file_content = await resize_image(file_content, max_width_resize, max_height_resize)

    # Eliminar la imagen de perfil anterior si existe
    current_profile_picture = existing_file

    if current_profile_picture:
        old_image_path = filepath + existing_file
        if os.path.exists(old_image_path):
            os.remove(old_image_path)

    with open(generated_name, "wb") as file:
        file.write(file_content)

    return token_name

async def delete_file(filepath, filename):
    """Elimina un archivo en base al path y nombre del archivo recibidos por parametro.
      Devuelve true si lo pudo eliminar, false en caso contrario."""
    file_to_delete = os.path.join(filepath, filename)
    print(file_to_delete)
    if os.path.exists(file_to_delete):
        os.remove(file_to_delete)
        return True
    else:
        return False