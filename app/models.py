from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP, Date

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

class AcademicExperience(Base):
    __tablename__ = "academic_experiences"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    institution = Column(String, nullable=False)
    field_of_study = Column(String, nullable=False)
    start_date = Column(Date, nullable=False) 
    end_date = Column(Date) #Puede no haber fecha de fin, significa que todavia esta en esa institucion
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))
class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    workTitle = Column(String, nullable=False)
    role = Column(String, nullable=False)
    start_date = Column(Date, nullable=False) 
    end_date = Column(Date) #Puede no haber fecha de fin, significa que todavia esta en ese trabajo
    producer = Column(String)
    projectUrl = Column(String)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))
    