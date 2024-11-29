from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric
from database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP, Date
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    fullname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True) #El unique es para que no haya mas de un email igual
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, server_default=text('false'))
    created_at = Column(TIMESTAMP(timezone=True),
                      nullable=False, server_default=text('now()'))
    
    #Al eliminarlo tmbien se eliminan los form_templates, proyectos y castings asociados                
    form_templates = relationship("FormTemplate", back_populates="owner", cascade="all, delete")
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    casting_calls = relationship("CastingCall", back_populates="owner", cascade="all, delete")



    profile_picture = Column(String)
    cv = Column(String)
    reel_link = Column(String)

    #Fotos del usuario
    chest_up_shot = Column(String) #foto plano pecho
    full_body_shot = Column(String) #foto plano entero
    profile_shot = Column(String) #foto perfil
    additional_shot_1 = Column(String)
    additional_shot_2 = Column(String)
 
    # Info basica, contacto y redes
    age = Column(Integer)
    gender = Column(String)
    residence_country = Column(String)
    locality = Column(String)
    nationality = Column(String)
    birth_date = Column(Date)
    phone_number = Column(String)
    phone_number_two = Column(String)
    instagram = Column(String)
    facebook = Column(String)
    youtube_channel = Column(String)
    website = Column(String)

    # Caracteristicas fisicas
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

    #Habilidades
    language_skills = Column(String)
    sports_skills = Column(String)
    instruments_skills = Column(String)
    other_skills = Column(String)
    is_singer = Column(Boolean)
    is_dancer = Column(Boolean)
    dance_types = Column(String)
    car_drivers_license = Column(Boolean)
    moto_drivers_license = Column(Boolean)
    skills_additionals = Column(String)

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
    
class FormTemplate(Base):
    __tablename__ = "form_templates"
    id = Column(Integer, primary_key=True, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, )
    form_template_title = Column(String, nullable=False)
    state = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    owner = relationship("User", back_populates="form_templates")


    # Definela relación con FormTemplateField
    form_template_fields = relationship("FormTemplateField", back_populates="form_template")
    #TODO: Luego se agregara el rol_id, es decir el rol al que esta asociado el formulario. QUIZAS NO

class FormTemplateField(Base):
    __tablename__ = "form_template_fields"
    id = Column(Integer, primary_key=True, nullable=False)
    form_template_id = Column(Integer, ForeignKey('form_templates.id', ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False) 
    order = Column(Integer, nullable=False)
    is_required = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Define la relación inversa
    form_template = relationship("FormTemplate", back_populates="form_template_fields")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, nullable=False)
    region = Column(String, nullable=False)
    state = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="projects")

    # Define la relación con Roles
    roles = relationship("Role", back_populates="project")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    assigned_user_id = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Define la relación inversa con el proyecto al que esta asociado
    project = relationship("Project", back_populates="roles")

class CastingCall(Base):
    __tablename__ = "casting_calls"
    id = Column(Integer, primary_key=True, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="casting_calls")
    title = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(Date)
    expiration_date = Column(Date)
    remuneration_type =  Column(String, nullable=False)
    casting_photos = Column(String)
    state = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class RoleByCastingCall(Base):
    __tablename__ = "roles_by_casting_calls"
    id = Column(Integer, primary_key=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete="CASCADE"), nullable=False)
    form_template_id = Column(Integer, ForeignKey('form_templates.id', ondelete="CASCADE"), nullable=False)
    casting_call_id = Column(Integer, ForeignKey('casting_calls.id', ondelete="CASCADE"), nullable=False)
    min_age_required = Column(Integer)
    max_age_required = Column(Integer)
    min_height_required = Column(Integer)
    max_height_required = Column(Integer)
    hair_colors_required = Column(String)
    additional_requirements = Column(String)
    has_limited_spots = Column(Boolean, nullable=False)
    spots_amount = Column(Integer)
    



    