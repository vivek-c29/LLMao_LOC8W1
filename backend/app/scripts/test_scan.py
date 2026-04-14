import asyncio
from bson import ObjectId
from app.database.mongo import scans_collection
from app.models.scan import ScanDB

async def test_insert_scan():
    scan = ScanDB(
        job_id=ObjectId(),  # Dummy job ID
        image="uploads/scans/dummy_scan.jpg",
        ai_result={"detected_problem": "Rusty pipe", "confidence": 0.92}
    )

    result = await scans_collection.insert_one(scan.model_dump(by_alias=True))
    print("✅ Inserted Scan ID:", result.inserted_id)

if __name__ == "__main__":
    asyncio.run(test_insert_scan())
