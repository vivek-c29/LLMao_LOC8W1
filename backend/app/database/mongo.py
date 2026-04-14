import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
db = client["sahayak_db"]

users_collection = db["users"]
workers_collection = db["workers"]
jobs_collection = db["jobs"]
scans_collection = db["scans"]
reviews_collection = db["reviews"]
work_history_collection = db["work_history"]