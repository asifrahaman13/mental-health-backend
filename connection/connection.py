import pymongo
from pymongo import MongoClient
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv("MONGODB_CONNECTION_URI")

client=MongoClient(mongodb_uri)

db = client["fastapi-test"]
collection = db["user"]