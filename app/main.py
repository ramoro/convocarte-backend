from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from routers import (
    user, 
    auth, 
    form_template, 
    academic_experience, 
    work_experience,
    project,
    casting_call,
    form,
    casting_postulation)
from fastapi.staticfiles import StaticFiles
from config import settings
import models

app = FastAPI()

origins = [
    settings.backend_url,
    settings.frontend_url,
    "https://convocarte-frontend.onrender.com",  # URL del frontend desplegado
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user.router)
app.include_router(academic_experience.router)
app.include_router(work_experience.router)
app.include_router(auth.router)
app.include_router(form_template.router)
app.include_router(form.router)
app.include_router(project.router)
app.include_router(casting_call.router)
app.include_router(casting_postulation.router)

@app.get("/")
def root():
    return {"Hello": "World"}

