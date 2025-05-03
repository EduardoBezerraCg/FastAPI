from typing import Optional
from fastapi.params import Body
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import numpy as np
from random import randrange
from psycopg2.extras import RealDictCursor
from typing import List

#from genSinteticData import generate_sintetic_data
from app.utils import hash
from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery
from . import schemas

#SQL Alchemy part
from app.db import models
from app.db.databaseSQLAlchemy import engine
models.Base.metadata.create_all(bind=engine)

#importing the routers
from app.routes.user import router as user_router
from app.routes.post import router as post_router


app = FastAPI()
np.random.seed(42)


#Root
app.include_router(user_router)
app.include_router(post_router)
@app.get("/")
def root():
    return {"data": "Welcome to our API!"}

