from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from routers import user, auth
import models


app = FastAPI()


models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"Hello": "World"}

