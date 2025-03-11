from utils import resize_image
from config import settings
import secrets
import shutil
import os

class LocalStorageManager:

    async def store_file(self, extension, filepath, new_file, resize, max_width_resize=0, max_height_resize=0, existing_file=None):
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

        generated_name = filepath + token_name
        file_url = settings.backend_url + generated_name[1:]

        return token_name, file_url
        

    async def delete_file(self, filepath, filename):
        """Elimina un archivo en base al path y nombre del archivo recibidos por parametro.
        Devuelve true si lo pudo eliminar, false en caso contrario."""
        file_to_delete = os.path.join(filepath, filename)
        print(file_to_delete)
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)
            return True
        else:
            return False
        
    def copy_file(self, source_path, filename_to_copy, destiny_path):
        """Recibe un path con la ubicacion del archivo a copiar, el nombre del archivo mismo 
        que necesita ser copiado, su ubicacion, y el path donde se va a almacenar la copia. 
        Se genera un nuevo nombre para el archivo con un valor hexadecimal random y se copia
        el archivo en el path de destino. Devuelve el nombre generado para el nuevo archivo."""
        extension = filename_to_copy.split('.')[-1]
        new_name = secrets.token_hex(10) + "." + extension

        full_destiny_path = os.path.join(destiny_path, new_name)
        shutil.copy(source_path + filename_to_copy, full_destiny_path)

        return new_name
