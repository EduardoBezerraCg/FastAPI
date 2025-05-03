from typing import Optional
from fastapi.params import Body
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import numpy as np
from random import randrange
from psycopg2.extras import RealDictCursor

#from genSinteticData import generate_sintetic_data
from app.db.database import makeQuery, makeQueryBySpecificValue, makeWriteQuery




app = FastAPI()
np.random.seed(42)

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    
    #rating: Optional[int] = None

my_posts = []

#Root

@app.get("/")
def root():
    return {"data": "Welcome to our API!"}


#Get posts
@app.get("/posts")
def get_posts():
    return makeQuery("""
        SELECT * FROM posts ORDER BY id;
    """)    
    

#Get post by ID
@app.get("/posts/{id}")
def get_post(id: int):
    post = makeQueryBySpecificValue("""
                                    
                                    SELECT * FROM posts WHERE id = %s;

                                    """, (id,))
    return {"post_detail": post}



#Post(create) a post
@app.post("/posts")
def create_post(post: Post):
    create_post_query = makeWriteQuery("""
        INSERT INTO posts (title, content, published)
        VALUES (%s, %s, %s) RETURNING *; """,(post.title, post.content, post.published))    
    
    return {"data": "post was created"}


#Delete
@app.delete("/posts/makeDeletions/{id}",status_code=204)
def delete_post(id:int):
    postDelete = makeWriteQuery("DELETE FROM public.posts WHERE id = %s RETURNING *;", (id,))

    return {"detail": "Post deleted"}



#UpdatePosts
@app.put("/posts/makeUpdates/{id}")
def update_post(id:int, post: Post):

    update_query = """
    UPDATE posts
    SET title = %s, content = %s, published = %s
    WHERE id = %s
    RETURNING *;
"""

    updated_post = makeWriteQuery(update_query, (post.title, post.content, post.published, id))

    return updated_post
