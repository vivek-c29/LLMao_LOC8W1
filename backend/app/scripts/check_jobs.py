import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client["sahayak_db"]
jobs_col = db["jobs"]

async def check_jobs():
    job = await jobs_col.find_one({})
    if job:
        print("Job found:")
        for k, v in job.items():
            print(f"{k}: {v} (type: {type(v)})")
    else:
        print("No jobs found in DB.")

if __name__ == "__main__":
    asyncio.run(check_jobs())
