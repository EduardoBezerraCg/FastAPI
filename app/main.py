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
    

#Get by ID
@app.get("/posts/{id}")
def get_post(id:int):

    post = makeQueryBySpecificValue(f"SELECT * FROM posts WHERE id = {id};")
    return {"post_detail": post}


#Post(create) a post
@app.post("/posts")
def create_post(post: Post):
    create_post_query = makeWriteQuery(f"""
        INSERT INTO posts (title, content, published)
        VALUES ('{post.title}', '{post.content}', {post.published}) RETURNING *;
    """)
    return {"data": "post was created"}



#Delete
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
        

@app.delete("/posts/makeDeletions/{id}",status_code=204)
def delete_post(id:int):
    postDelete = makeWriteQuery(f"DELETE FROM public.posts WHERE id = {id};")

    return


#UpdatePosts
@app.put("/posts/makeUpdates/{id}")
def update_post(id:int, post: Post):

    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=404, detail=f"post with id: {id} does not exist")
    
    post_dict = post.model_dump()
    post_dict["id"] = id
    my_posts[index] = post_dict

    return {"data": "post was updated"}