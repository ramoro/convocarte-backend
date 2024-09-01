from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    fullname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True) #El unique es para que no haya mas de un email igual
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, server_default=text('false'))
    created_at = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))
    profile_picture = Column(String)
    