from database import get_db
import logging
from datetime import date

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
    
        users_to_delete = db.query(models.User).filter(
            models.User.is_verified == False,
            models.User.created_at < cutoff_time
        ).all()
        
        for user in users_to_delete:
            db.delete(user)
        
        db.commit()
        logger.info(f"Deleted {len(users_to_delete)} unverified users created before {cutoff_time}")

async def change_state_expired_casting_calls():
    async with get_db_context() as db:
        today = date.today()

        updated_castings = db.query(models.CastingCall)\
        .filter(models.CastingCall.expiration_date <= today)\
        .filter(models.CastingCall.state != "Vencido")\
        .update({models.CastingCall.state: "Vencido"}, synchronize_session=False)

        db.commit()
        logger.info(f"Updated {updated_castings} as expired")


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