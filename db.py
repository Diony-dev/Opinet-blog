from flask_pymongo import PyMongo

mongo = None

def init_db(app):
    global mongo
    mongo = PyMongo(app)

def get_db():
    return mongo.db