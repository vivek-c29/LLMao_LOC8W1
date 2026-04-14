import asyncio
from bson import ObjectId
from app.database.mongo import reviews_collection
from app.models.review import ReviewDB

async def test_insert_review():
    review = ReviewDB(
        job_id=ObjectId(),    # Dummy job ID
        worker_id=ObjectId(), # Dummy worker ID
        rating=5,
        comment="Excellent service, very professional."
    )

    result = await reviews_collection.insert_one(review.model_dump(by_alias=True))
    print("✅ Inserted Review ID:", result.inserted_id)

if __name__ == "__main__":
    asyncio.run(test_insert_review())
