import os
from flask import Flask
from redis import Redis

app = Flask(__name__)
redis = Redis()

@app.route('/')
def hello():
    return 'Hello World!'


