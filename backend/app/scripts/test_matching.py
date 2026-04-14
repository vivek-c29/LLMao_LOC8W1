import asyncio
from app.database.mongo import jobs_collection, workers_collection, users_collection
from app.utils.matching import match_workers

async def test_matching_db():
    # 1. Fetch the most recent job to test against
    job = await jobs_collection.find_one(sort=[("_id", -1)])
    if not job:
        print("❌ No jobs found in database. Please run test_job.py first.")
        return

    job_location = job.get("location", {})
    required_skill = job.get("skill_required")
    problem = job.get("problem", "N/A")
    
    print(f"--- Matching Workers for Job: '{problem}' ---")
    print(f"    Required Skill: {required_skill}")
    print(f"    Location: {job_location}")
    print("-" * 40)

    # 2. Fetch all workers from DB
    workers_cursor = workers_collection.find({})
    workers = await workers_cursor.to_list(length=100)
    
    if not workers:
        print("❌ No workers found in database. Please run test_worker.py first.")
        return

    # Fetch names from users collection for these workers
    for worker in workers:
        user = await users_collection.find_one({"_id": worker["user_id"]})
        if user:
            worker["name"] = user.get("name", "Unknown")

    # 3. Use the matching utility
    results = match_workers(job_location, required_skill, workers)

    if not results:
        print(f"⚠️ No workers found matching skill: '{required_skill}'")
        return

    # 4. Print Ranked Results
    for i, res in enumerate(results, 1):
        print(f"{i}. Worker: {res.get('name', 'N/A')} (ID: {res['worker_id']})")
        print(f"   Rating: {res['rating']} | Distance: {res['distance_km']}km | Proximity Score: {res['proximity_score']}")
        print(f"   Final Score: {res['final_score']}")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(test_matching_db())
