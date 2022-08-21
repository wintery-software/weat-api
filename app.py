from flask import Flask

import pandas as pd
import random

app = Flask(__name__)


@app.route('/')
def hello_world():
    return {'message': 'hi'}


@app.route('/lucky')
def lucky():
    names = pd.read_csv('restaurants.csv')['name'].tolist()
    picked_name = random.choice(names)

    return picked_name
