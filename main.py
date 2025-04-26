from fastapi.params import Body
from fastapi import FastAPI

from genSinteticData import generate_sintetic_data


import numpy as np

app = FastAPI()
np.random.seed(42)


@app.get("/")
def root():
    return {"data": "Welcome to our API!"}



@app.get("/posts")
def get_posts():
    query = generate_sintetic_data()
    return {"random_numbers": query.tolist()}


@app.post("/createPots")
def create_post(payLoad: dict = Body(...)):
    print(payLoad)
    return {"message": f"{payLoad['title']} content: {payLoad['content']}"}