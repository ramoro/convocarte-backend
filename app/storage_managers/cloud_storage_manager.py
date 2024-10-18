
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account
from utils import resize_image
import secrets
from config import settings

API_NAME='drive'
API_VERSION='v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
CLOUD_STORAGE_URL = "https://lh3.google.com/u/0/d/"
CLOUD_STORAGE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id="

class CloudStorageManager:
    """Clase que se encarga de almacenar y eliminar archivos en un almacenamiento en Google Drive."""
    def __init__(self):
        # Configuración de Google Drive
        credentials = service_account.Credentials.from_service_account_info(settings.google_credentials_dict, scopes=SCOPES)
        self.drive_service = build('drive', 'v3', credentials=credentials)

    async def store_file(self, extension, filepath, new_file, existing_file, resize, max_width_resize=0, max_height_resize=0):
        # Generar el nombre del archivo en hexadecimal
        token_name = secrets.token_hex(10) + "." + extension

        # Leer el contenido del nuevo archivo
        file_content = await new_file.read()

        # Redimensionar si es necesario
        if resize:
            file_content = await resize_image(file_content, max_width_resize, max_height_resize)

        # Subir el nuevo archivo a Google Drive
        file_metadata = {
            'name': token_name,
            'parents': [filepath]
        }

        # Definir el mimetype
        if extension.lower() in ['jpg', 'jpeg', 'png']:
            mimetype = f'image/{extension}'
        elif extension.lower() == 'pdf':
            mimetype = 'application/pdf'
        
        media = MediaInMemoryUpload(file_content, mimetype=mimetype)
        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        file_id = file.get('id')
        print(f"{file_metadata['name']} uploaded successfully to Google Drive with id {file_id}")

        #Con el id se ubica al archivo en google drive, por eso almacenamos su id
        name_to_store_in_db = file_id
        #Si es pdf el link que se le agrega es el de descarga
        if extension.lower() == 'pdf':
            file_url = CLOUD_STORAGE_DOWNLOAD_URL + file_id
        else:
            file_url = CLOUD_STORAGE_URL + file_id

        return name_to_store_in_db, file_url
    
    async def delete_file(self, filepath, filename):
        """Elimina un archivo de Google Drive a partir de su id, que esta en el filename."""
        try:
            file_id = filename
            self.drive_service.files().delete(fileId=file_id).execute()
            print(f"Successfully deleted file/folder with ID: {file_id}")
            return True
        except Exception as e:
            print(f"Error deleting file/folder with ID: {file_id}")
            print(f"Error details: {str(e)}")
            return False

