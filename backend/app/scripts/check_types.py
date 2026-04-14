import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client["sahayak_db"]
reviews_col = db["reviews"]

async def check_reviews():
    review = await reviews_col.find_one({})
    if review:
        print("Review found:")
        for k, v in review.items():
            print(f"{k}: {v} (type: {type(v)})")
    else:
        print("No reviews found in DB.")

if __name__ == "__main__":
    asyncio.run(check_reviews())
