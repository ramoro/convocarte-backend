from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric
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
    weight = Column(Numeric(10, 2))
    height = Column(Numeric(10, 2))
    eyes_color = Column(String)
    skin_color = Column(String)
    waist_measurement = Column(Numeric(10, 2))
    hip_measurement = Column(Numeric(10, 2))
    bust_measurement = Column(Numeric(10, 2))
    hair_color = Column(String) 
    pant_size = Column(String) #Los talles pueden ser tanto strings (M/L/XL) como numeros (42/44/45)
    tshirt_size = Column(String)
    jacket_size = Column(String)
    shoes_size = Column(String)
    hands = Column(String)
    feet = Column(String)
    teeth = Column(String)
    braces = Column(Boolean)
    tattoos = Column(Boolean)
    tattoos_area = Column(String)
    piercings = Column(Boolean)
    piercings_area = Column(String)
    physical_characs_extra_info = Column(String)

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
    work_title = Column(String, nullable=False)
    role = Column(String, nullable=False)
    start_date = Column(Date, nullable=False) 
    end_date = Column(Date) #Puede no haber fecha de fin, significa que todavia esta en ese trabajo
    producer = Column(String)
    project_url = Column(String)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))
    