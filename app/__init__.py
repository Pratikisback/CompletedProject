from flask import Flask
from flask_restful import Api, Resource
from pymongo import MongoClient
import smtplib
from flask_jwt_extended import JWTManager
from app.celery_config.configs_celery import create_celery


app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://mongodb:27017")
# client = MongoClient("mongodb://localhost:27017")
db = client['UserDB']
collection = db['UserCollection']
app.config["JWT_SECRET_KEY"] = "zanchanotachi"
jwt_manager = JWTManager(app)

app.config['broker_url'] = 'amqp://amqp:5672/'

app.config['backend'] = 'amqp://amqp:5672/'

app.config['event_serializer'] = 'json'
app.config['result_serializer'] = 'json'
app.config['task_serializer'] = 'json'
celery = create_celery(app)
