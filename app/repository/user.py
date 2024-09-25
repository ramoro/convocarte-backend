import models
from database import get_db
from sqlalchemy.orm import Session

class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email):
        #cursor.execute("""INSERT INTO users (username, fullname, email, password) 
        #              VALUES (%s, %s, %s, %s) RETURNING *""", (user.username, user.fullname, user.email, user.password ))
        #new_user = cursor.fetchone()
        #conn.commit()
        return self.db.query(models.User).filter((models.User.email == email)).first()
    
    def get_user_by_id(self, id):
        return self.db.query(models.User).filter(models.User.id == id).first() #Se usa first y no all porque se sabe q por id es unico, sino seguiria buscando y gastaria mas tiempo
    
    def add_new_user(self, dict_user):
        new_user = models.User(
            #username=user.username, fullname=user.fullname, email=user.email, 
            #password=user.password
            **dict_user) #Pasamos el modelo de pydantic a diccionario y luego lo desempaquetamos
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user) #devuelve lo que se guardo recien y se almacena en new_user

        return new_user
    
    def update_user(self, id, data):
        self.db.query(models.User).filter(models.User.id == id).update(data, synchronize_session=False)
        self.db.commit()