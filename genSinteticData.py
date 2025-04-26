import numpy as np


def generate_sintetic_data():
    random_numbers = np.random.rand(5)
    return {"random_numbers": random_numbers.tolist()}