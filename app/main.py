
from fastapi import FastAPI, status
from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery

#Teste123

#SQL Alchemy part
from app.db import models
from app.db.databaseSQLAlchemy import engine
models.Base.metadata.create_all(bind=engine)

#importing the routers
from app.routes.user import router as user_router
from app.routes.post import router as post_router
from app.routes.auth import router as auth


app = FastAPI()



#Root
app.include_router(user_router)
app.include_router(post_router)
app.include_router(auth)

@app.get("/")
def root():
    return {"data": "Welcome to our API!"}

