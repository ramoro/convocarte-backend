from database import get_db
import logging
from repository.project import ProjectRepository
from repository.casting_call import CastingCallRepository
from repository.user import UserRepository


##Para programar tareas
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("convocarte-scheduled-tasks.log"),   
    logging.StreamHandler()],
    
)
logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models

async def clean_old_unverified_users():
    async with get_db_context() as db:
        
        cutoff_time = datetime.utcnow() - timedelta(hours=24)

        user_repository = UserRepository(db)

        deleted_users = user_repository.delete_unverified_users_cutoff_time_expired(cutoff_time)

        logger.info(f"Deleted {len(deleted_users)} unverified users created before {cutoff_time}")

async def change_state_expired_casting_calls():
    async with get_db_context() as db:

        casting_call_repository = CastingCallRepository(db)

        expired_castings = casting_call_repository.update_expired_casting_calls()
        
        project_repository = ProjectRepository(db)

        #Actualiza uso del proyecto si corresponde, de estar publicado a sin usar
        for casting in expired_castings:
            logger.info(f"estado {casting.state}")
            project_repository.update_project_state(casting.project)
            logger.info(f"estado projecto {casting.project.is_used}")


        logger.info(f"Updated {len(expired_castings)} as expired")


# Context manager para usar get_db() de forma async
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_context():
    db_gen = get_db()
    db = next(db_gen)
    try:
        yield db
    finally:
        db.close()