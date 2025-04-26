from fastapi import FastAPI
import numpy as np

app = FastAPI()
np.random.seed(42)


@app.get("/")
def root():
    random_numbers = np.random.rand(5)  # Generate an array of 5 random numbers
    return {"random_numbers": random_numbers.tolist()}


@app.get("/posts")
def get_posts():
    return {"data": "This is your posts"}