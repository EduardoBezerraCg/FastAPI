from typing import Optional
from fastapi.params import Body
from fastapi import FastAPI, HTTPException, status, APIRouter
from pydantic import BaseModel
import numpy as np
from random import randrange
from psycopg2.extras import RealDictCursor
from typing import List

#from genSinteticData import generate_sintetic_data
from app.utils import hash
from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery
from .. import schemas

#SQL Alchemy part
from app.db import models
from app.db.databaseSQLAlchemy import engine

router = APIRouter()

############################       Posts part        ######################################
#Get posts
@router.get("/posts", status_code=status.HTTP_200_OK,response_model=List[schemas.PostResponse])
def get_posts():
    return makeQuery("""
        SELECT * FROM posts ORDER BY id;
    """)    
    

#Get post by ID
@router.get("/posts/{id}")
def get_post(id: int):
    post = makeQueryBySpecificValue("""
                                    
                                    SELECT * FROM posts WHERE id = %s;

                                    """, (id,))
    return {"post_detail": post}



#Post(create) a post
@router.post("/posts", response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate):
    create_post_query = makeWriteQuery("""
        INSERT INTO posts (title, content, published)
        VALUES (%s, %s, %s) RETURNING *; """,(post.title, post.content, post.published))    
    
    return create_post_query


#Delete
@router.delete("/posts/makeDeletions/{id}",status_code=204)
def delete_post(id:int):
    postDelete = makeWriteQuery("DELETE FROM public.posts WHERE id = %s RETURNING *;", (id,))

    return {"detail": "Post deleted"}



#UpdatePosts
@router.put("/posts/makeUpdates/{id}")
def update_post(id:int, post: schemas.PostCreate):

    update_query = """
    UPDATE posts
    SET title = %s, content = %s, published = %s
    WHERE id = %s
    RETURNING *;
"""

    updated_post = makeWriteQuery(update_query, (post.title, post.content, post.published, id))

    return updated_post