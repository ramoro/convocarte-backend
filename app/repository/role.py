import models
from sqlalchemy.orm import Session

class RoleRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_role_by_id(self, role_id):
        return self.db.query(models.Role).filter((models.Role.id == role_id)).first()
