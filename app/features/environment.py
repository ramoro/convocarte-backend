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
    
# def after_scenario(context, scenario):
#     """Limpieza después de cada escenario."""
#     session = context.database
#     try:
#         # Deshabilitar restricciones de clave foránea temporalmente
#         session.execute("SET session_replication_role = 'replica';")
        
#         # Borrar registros de las tablas en orden correcto
#         tables = [
#             "exposed_roles", "form_fields", "forms",
#             "form_template_fields", "form_templates", "roles",
#             "casting_calls", "projects"
#         ]
        
#         for table in tables:
#             session.execute(f"DELETE FROM {table};")
        
#         # Restaurar restricciones
#         session.execute("SET session_replication_role = 'origin';")
#         session.commit()
#     except Exception as e:
#         session.rollback()
#         raise e
#     finally:
#         session.close()
def after_scenario(context, scenario):
    """Limpieza después de cada escenario usando DELETE."""
    session = context.database
    try:
        # Borrar registros de las tablas en orden correcto
        session.execute("DELETE FROM open_roles;")
        session.execute("DELETE FROM form_fields;")
        session.execute("DELETE FROM forms;")
        session.execute("DELETE FROM form_template_fields;")
        session.execute("DELETE FROM form_templates;")
        session.execute("DELETE FROM roles;")
        session.execute("DELETE FROM casting_calls;")
        session.execute("DELETE FROM projects;")
        session.execute("DELETE FROM messages;")
        session.execute("DELETE FROM casting_postulations;")


        
        # Confirmar los cambios
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()