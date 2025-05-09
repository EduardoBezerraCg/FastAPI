from fastapi import status, APIRouter, HTTPException, Depends

from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Users Section/Properties"],
    responses={404: {"description": "Not found"}}
)

#from genSinteticData import generate_sintetic_data
from app.utils import hash
from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery
from .. import schemas

#SQL Alchemy part
from app.db import models
from app.db.databaseSQLAlchemy import engine
from .. import schemas, oauth2

############################       Users part        ######################################

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.UserOut])
def get_users(current_user: dict = Depends(oauth2.get_current_user)):
    return makeQuery("""
        SELECT * FROM users ORDER BY id;
    """) 

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate):
    #Hash the password
    hashed_password = hash(user.password)
    user.password = hashed_password

    new_user = makeWriteQuery("""
        INSERT INTO users (email, password)
        VALUES (%s, %s) RETURNING *; 
                              """,(user.email, user.password))  
    return new_user


@router.get("/specificUser/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def get_user(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    user = makeQueryBySpecificValue(""" 
            SELECT * FROM users WHERE id = %s;
            """, (id,))
    return user