import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client["sahayak_db"]

users_col = db["users"]
workers_col = db["workers"]
jobs_col = db["jobs"]
scans_col = db["scans"]
reviews_col = db["reviews"]
work_history_col = db["work_history"]

async def seed():
    print("Clearing existing data...")
    await users_col.delete_many({})
    await workers_col.delete_many({})
    await jobs_col.delete_many({})
    await scans_col.delete_many({})
    await reviews_col.delete_many({})
    await work_history_col.delete_many({})

    print("Seeding Users...")
    user_ids = []
    worker_user_ids = []
    
    # 2 Clients
    clients = [
        {"name": "Rahul Sharma", "phone": "9876543210", "password": "hashed_pw", "role": "client", "language": "en", "location": {"lat": 18.5204, "lng": 73.8567}, "created_at": datetime.utcnow()},
        {"name": "Priya Patil", "phone": "9876543211", "password": "hashed_pw", "role": "client", "language": "hi", "location": {"lat": 18.5204, "lng": 73.8567}, "created_at": datetime.utcnow()},
    ]
    for c in clients:
        res = await users_col.insert_one(c)
        user_ids.append(res.inserted_id)

    # 4 Workers (Users)
    workers_users = [
        {"name": "Amit Electrician", "phone": "9876543212", "password": "hashed_pw", "role": "worker", "language": "mr", "location": {"lat": 18.5207, "lng": 73.8560}, "created_at": datetime.utcnow()},
        {"name": "Suresh Plumber", "phone": "9876543213", "password": "hashed_pw", "role": "worker", "language": "en", "location": {"lat": 18.5210, "lng": 73.8555}, "created_at": datetime.utcnow()},
        {"name": "Vikas Electrician (Far)", "phone": "9876543214", "password": "hashed_pw", "role": "worker", "language": "en", "location": {"lat": 18.6000, "lng": 73.9000}, "created_at": datetime.utcnow()},
        {"name": "Karan Carpenter", "phone": "9876543215", "password": "hashed_pw", "role": "worker", "language": "hi", "location": {"lat": 18.5205, "lng": 73.8565}, "created_at": datetime.utcnow()},
    ]
    for w in workers_users:
        res = await users_col.insert_one(w)
        worker_user_ids.append(res.inserted_id)

    print("Seeding Workers...")
    worker_ids = []
    worker_data = [
        {
            "user_id": worker_user_ids[0],
            "skills": ["Electrician", "AC Repair"],
            "rating": 4.5,
            "total_jobs": 10,
            "total_earnings": 5000.0,
            "total_jobs_completed": 8,
            "experience_years": 5,
            "availability": True,
            "verified": True,
            "location": {"lat": 18.5207, "lng": 73.8560},
            "created_at": datetime.utcnow()
        },
        {
            "user_id": worker_user_ids[1],
            "skills": ["Plumber", "Drainage"],
            "rating": 4.0,
            "total_jobs": 5,
            "total_earnings": 2500.0,
            "total_jobs_completed": 4,
            "experience_years": 3,
            "availability": True,
            "verified": False,
            "location": {"lat": 18.5210, "lng": 73.8555},
            "created_at": datetime.utcnow()
        },
        {
            "user_id": worker_user_ids[2],
            "skills": ["Electrician"],
            "rating": 4.8,
            "total_jobs": 20,
            "total_earnings": 15000.0,
            "total_jobs_completed": 18,
            "experience_years": 8,
            "availability": True,
            "verified": True,
            "location": {"lat": 18.6000, "lng": 73.9000},
            "created_at": datetime.utcnow()
        },
        {
            "user_id": worker_user_ids[3],
            "skills": ["Carpenter"],
            "rating": 3.5,
            "total_jobs": 2,
            "total_earnings": 800.0,
            "total_jobs_completed": 1,
            "experience_years": 1,
            "availability": True,
            "verified": False,
            "location": {"lat": 18.5205, "lng": 73.8565},
            "created_at": datetime.utcnow()
        }
    ]
    for wd in worker_data:
        res = await workers_col.insert_one(wd)
        worker_ids.append(res.inserted_id)

    print("Seeding Jobs...")
    job_ids = []
    jobs = [
        {
            "client_id": user_ids[0],
            "input_type": "text",
            "input_ref": "Fan not working",
            "skill_required": "Electrician",
            "problem": "Ceiling fan is making noise and not spinning at full speed",
            "problem_type": "Electrician",
            "description": "Fan not working",
            "urgency": 5.0,
            "status": "posted",
            "location": {"lat": 18.5204, "lng": 73.8567},
            "language": "en",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "client_id": user_ids[1],
            "input_type": "voice",
            "input_ref": "voice_ref_123",
            "skill_required": "Plumber",
            "problem": "Leaking tap in kitchen",
            "problem_type": "Plumber",
            "description": "Voice recording about plumbing issue",
            "urgency": 8.0,
            "status": "accepted",
            "worker_id": worker_ids[1],
            "quoted_price": 350.0,
            "location": {"lat": 18.5204, "lng": 73.8567},
            "language": "hi",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    for j in jobs:
        res = await jobs_col.insert_one(j)
        job_ids.append(res.inserted_id)

    print("Seeding Scans...")
    scan = {
        "job_id": job_ids[0],
        "image_url": "dummy_fan_issue.jpg",
        "detected_problem": "Ceiling fan blade bent",
        "suggested_worker_type": "Electrician",
        "urgency": 5.0,
        "ai_result": {"status": "analyzed"},
        "created_at": datetime.utcnow()
    }
    await scans_col.insert_one(scan)

    print("Seeding Reviews & History...")
    # Add a history for Suresh
    history = {
        "worker_id": worker_ids[1],
        "job_id": ObjectId(), # Random dummy job
        "completed_at": datetime.utcnow(),
        "earnings": 500.0
    }
    await work_history_col.insert_one(history)

    # Add a review for Suresh
    review = {
        "job_id": job_ids[1],
        "client_id": user_ids[1],
        "worker_id": worker_ids[1],
        "rating": 5,
        "comment": "Quick and efficient!",
        "created_at": datetime.utcnow()
    }
    await reviews_col.insert_one(review)

    print(f"\nSeeding complete!")
    print(f"Client IDs: {[str(i) for i in user_ids]}")
    print(f"Worker IDs: {[str(i) for i in worker_ids]}")
    print(f"Job IDs:    {[str(i) for i in job_ids]}")

if __name__ == "__main__":
    asyncio.run(seed())
