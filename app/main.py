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
    casting_postulation,
    message)
from fastapi.staticfiles import StaticFiles
from config import settings
import models
import asyncio
from scheduled_tasks import clean_old_unverified_users, change_state_expired_casting_calls
from utils import run_scheduled_function


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
app.include_router(message.router)

@app.get("/")
def root():
    return {"Hello": "World"}

#Corrida de tareas programadas:
#clean_unverified_users: limpia usuarios que se crearon cuenta y no la verificaron hace mas de 24 hs
#change_state_expired_casting_calls: cambia estado a "Vencido" a los castings que ya vencio su fecha de expiracion
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_scheduled_function(clean_old_unverified_users, hour=8, minute=0))
    asyncio.create_task(run_scheduled_function(change_state_expired_casting_calls, hour=0, minute=0))