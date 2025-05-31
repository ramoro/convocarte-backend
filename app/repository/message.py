import json
import models
from sqlalchemy.orm import Session, aliased
from sqlalchemy import text

class MessageRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_message_by_id(self, message_id):
        """Recibe el id de un mensaje y devuelve el mensaje correspondiente."""
        message = self.db.query(models.Message).filter(models.Message.id == message_id).first()
        return message

    def add_new_message(self, message):
        """Recibe un diccionario con la informacion de un mensaje enviado en una postulacion.
        Crea el mensaje en la BDD y devuelve el objeto creado."""
        new_message = models.Message(**message) 

        self.db.add(new_message)
        self.db.commit()
        self.db.refresh(new_message) 

        return new_message
    
    def get_messages_by_postulation_id(self, postulation_id):
        """Recibe el id de una postulacion y devuelve todos los mensajes asociados
        a esa postulacion, junto con el fullname y la foto de perfil del emisor,
        en forma de tupla."""
        
        sender_alias = aliased(models.User)
        
        messages = self.db.query(
            models.Message,
            sender_alias.fullname,
            sender_alias.profile_picture
        ).join(
            sender_alias, models.Message.sender_id == sender_alias.id
        ).filter(
            models.Message.postulation_id == postulation_id
        ).order_by(
            models.Message.created_at
        ).all()

        return messages
    
    def update_message_partially(self, data, message_id):
        self.db.query(models.Message).filter(models.Message.id == message_id).update(data, synchronize_session=False)
        self.db.commit()

    def add_new_message_for_many_users(self, content, files, postulations, placeholder_to_replace, sender_id):
        """Recibe el contenido del mensaje, un texto con los archivos adjuntos, el id del emisor, un placeholder
        que sera reemplazado con el nombre del usuario postulado y una estructura JSON postulations de la forma:
        [{"postulationId":<id>,"postulatedUserId":<id>,"postulatedUserName":"<name>"}]. Ejecuta un Store Procedure
        que crea el mensaje para todos los usuarios postulados que vienen en postulations. Devuelve True en caso
        de exito, sino devuelve False y el error ocurrido.
        """
        sp_call = 'CALL "MSG_CreateForManyUsers"(:content, :files, :postulations, :sender_id, :placeholder)'
        try: 
            self.db.execute(
                text(sp_call),
                {
                    "content": content,
                    "files": files,
                    "postulations": postulations,
                    "sender_id": sender_id,
                    "placeholder": placeholder_to_replace,
                }
            )
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return False, e
        return True, None