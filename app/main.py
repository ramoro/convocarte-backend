from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from routers import user, auth
from fastapi.staticfiles import StaticFiles
from config import settings
import models
import time

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

time.sleep(20)

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"Hello": "World"}

