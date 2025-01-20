from config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import models

TEST_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@\
{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def before_all(context):
    """Configuración antes de todas las pruebas."""
    # Crear tablas
    models.Base.metadata.create_all(bind=engine)
    # Conectar a la base de datos

def after_all(context):
    """Limpieza después de todas las pruebas."""
    # Eliminar tablas
    models.Base.metadata.drop_all(bind=engine)

def before_scenario(context, scenario):
    """Configuración antes de cada escenario."""
    context.database = SessionLocal()

def after_scenario(context, scenario):
    """Limpieza después de cada escenario."""
    # No alcanza con el delete on cascade, asi que se eliminan estas tablas
    # en este orden para que no haya problemas de foreign key
    session = context.database

    try:
        # Truncar las tablas en orden correcto para evitar conflictos de claves foráneas
        # No se borra la tabla de usuarios para no estar creando a cada rato el mismo usuario
        # Total siempre se va a necesitar un usuario creado
        session.execute("TRUNCATE TABLE form_template_fields CASCADE;")
        session.execute("TRUNCATE TABLE form_templates CASCADE;")
        session.execute("TRUNCATE TABLE form_fields CASCADE;")
        session.execute("TRUNCATE TABLE forms CASCADE;")
        session.execute("TRUNCATE TABLE roles CASCADE;")
        session.execute("TRUNCATE TABLE casting_calls CASCADE;")
        session.execute("TRUNCATE TABLE exposed_roles CASCADE;")
        session.execute("TRUNCATE TABLE projects CASCADE;")
        session.execute("TRUNCATE TABLE users CASCADE;")

        
        # Confirmar los cambios
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()