import asyncio
from app.database.mongo import jobs_collection, workers_collection
from bson import ObjectId

async def check_types():
    print("--- ID Type Check ---")
    
    # Check Jobs
    job = await jobs_collection.find_one()
    if job:
        job_id = job.get("_id")
        print(f"Job ID: {job_id} | Type: {type(job_id)}")
    else:
        print("No jobs found.")

    # Check Workers
    worker = await workers_collection.find_one()
    if worker:
        worker_id = worker.get("_id")
        user_id = worker.get("user_id")
        print(f"Worker ID: {worker_id} | Type: {type(worker_id)}")
        print(f"Worker User ID: {user_id} | Type: {type(user_id)}")
    else:
        print("No workers found.")

if __name__ == "__main__":
    asyncio.run(check_types())
