from passlib.context import CryptContext
import re
from PIL import Image
import io

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_valid_password(password: str, password_confirmation: str):
    """Recibe dos password, valida que sean iguales y que cumplan con los requisitos de tener al menos 8
    caracteres, un numero, una mayuscula, una minuscula y un caracter especial. Devuelve true en caso de
    cumplir con los requisitos, false en caso contrario."""
    return password == password_confirmation and re.match(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#,\-_$%&*]).{8,}$", password
    )


def hash(password: str):
    """Recibe una contraseña y devuelve la misma pero hasheada."""
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    """Recibe una contraseña y una contraseña hasheada. Devuelve true en caso de que sean las mismas.
    False en caso contrario."""
    return pwd_context.verify(
        plain_password, hashed_password
    )  # Usar la plain password para hashearla y compararla con la password hasheada obtenida de la bdd


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