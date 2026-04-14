import asyncio
import httpx
from bson import ObjectId

BASE_URL = "http://127.0.0.1:8000"

async def test_reviews():
    async with httpx.AsyncClient() as client:
        # 1. Create a dummy job, user, and worker first (assumes DB has some data or we use fixed IDs for testing)
        user_id = str(ObjectId())
        worker_id = str(ObjectId())
        job_id = str(ObjectId())
        
        print(f"Testing reviews for worker: {worker_id}")
        
        # 2. Add a review
        review_data = {
            "job_id": job_id,
            "reviewer_id": user_id,
            "worker_id": worker_id,
            "rating": 5,
            "comment": "Excellent work!"
        }
        resp = await client.post(f"{BASE_URL}/reviews/", json=review_data)
        print(f"Post Review: {resp.status_code} - {resp.json()}")

        # 3. Check worker stats
        resp = await client.get(f"{BASE_URL}/reviews/worker/{worker_id}/stats")
        print(f"Worker Stats: {resp.status_code} - {resp.json()}")

if __name__ == "__main__":
    try:
        asyncio.run(test_reviews())
    except Exception as e:
        print(f"Error: {e}")
