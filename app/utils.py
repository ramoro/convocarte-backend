from passlib.context import CryptContext
import re
from PIL import Image
import io
import logging
import asyncio
from datetime import datetime, timedelta

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

##Para programar tareas
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("convocarte-scheduled-tasks.log"),   
    logging.StreamHandler()],
    
)
logger = logging.getLogger(__name__)

def calculate_seconds(hour, minute, day=None, weekday=None):
    """
    Recibe cierta hora y minuto, y da la posibilidad de recibir un dia y dia de semana.
	Retorna la cantidad de segundos que hay entre el momento de ejecucion de la funcion y el dia de la semana,
    la hora y el minuto indicados.
	Si no se indica el dia (weekday), se tomara el dia actual.
	"""

    now = datetime.now()
    if day is not None:
        target = datetime(year=now.year, month=now.month, day=day, hour=hour, minute=minute)
        if target < now:
            if now.month == 12:
                target = datetime(year=now.year + 1, month=1, day=day, hour=hour, minute=minute)
            else:
                target = datetime(year=now.year, month=now.month + 1, day=day, hour=hour, minute=minute)
    elif weekday is None:
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
    else:
        days_until_target = (weekday - now.weekday()) % 7
        if days_until_target == 0:
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target <= now:
                days_until_target = 7
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_until_target)

    return (target - now).total_seconds()

async def run_scheduled_function(function, hour, minute, day=None, weekday=None):
    """
    Recibe una funcion y la ejecuta todos los dias (o cada semana si se usa el parametro dia_semana) 
    en la hora y minuto indicados.
	"""

    await function()
    while True:
        seconds_until_next = calculate_seconds(hour, minute, day, weekday)
        logger.info(f"Next execution of {function.__name__} in {int(seconds_until_next)} seconds")
        await asyncio.sleep(seconds_until_next)
        await function()