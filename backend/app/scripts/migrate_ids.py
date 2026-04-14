import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client["sahayak_db"]

async def migrate_collection(col_name, id_fields):
    col = db[col_name]
    print(f"Migrating {col_name}...")
    cursor = col.find({})
    async for doc in cursor:
        updates = {}
        for field in id_fields:
            val = doc.get(field)
            if isinstance(val, str) and ObjectId.is_valid(val):
                updates[field] = ObjectId(val)
        
        # Also check main _id if it's a string (though MongoBaseModel usually handles this)
        if isinstance(doc.get("_id"), str) and ObjectId.is_valid(doc["_id"]):
            # This is tricky as we can't easily change _id. We'd have to re-insert.
            # But usually it's the other fields that are strings.
            pass

        if updates:
            await col.update_one({"_id": doc["_id"]}, {"$set": updates})
            print(f"  Updated doc {doc['_id']} fields: {list(updates.keys())}")

async def main():
    # Corrections for Reviews
    await migrate_collection("reviews", ["job_id", "reviewer_id", "worker_id"])
    
    # Corrections for Jobs
    await migrate_collection("jobs", ["user_id", "assigned_worker_id"])
    
    # Corrections for Workers
    await migrate_collection("workers", ["user_id"])
    
    # Corrections for Scans
    await migrate_collection("scans", ["job_id"])

    # Corrections for Work History
    await migrate_collection("work_history", ["worker_id", "job_id"])

    print("✅ Migration complete!")

if __name__ == "__main__":
    asyncio.run(main())
