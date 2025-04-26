from typing import Optional
from fastapi.params import Body
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from random import randrange

from genSinteticData import generate_sintetic_data



app = FastAPI()
np.random.seed(42)

class Post(BaseModel):
    title: str
    bodyOfThePost: str
    published: bool = True
    rating: Optional[int] = None

my_posts = [{
    "title": "title of post 1", 
    "content": "content of post 1", 
    "id": 1
    },
    {"title": "favorite foods", 
     "content": "I like pizza", 
     "id": 2
    }]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

#Root

@app.get("/")
def root():
    return {"data": "Welcome to our API!"}


#Get's
@app.get("/posts")
def get_posts():
    query = generate_sintetic_data()
    #return {"random_numbers": query.tolist()}
    return {"data": my_posts}


#Get by ID
@app.get("/posts/{id}")
def get_post(id:int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=404, detail=f"post with id: {id} was not found")
    return {"post_detail": post}

#Posts
@app.post("/posts")
def create_post(post: Post):
    post_dict = post.model_dump()
    post_dict["id"] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

