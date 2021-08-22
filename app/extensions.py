from flask_pymongo import PyMongo
from flask import Flask

# Setup MongoDB here
mongo = PyMongo(Flask(__name__), uri="mongodb://localhost:27017/database")
