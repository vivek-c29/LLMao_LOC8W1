import asyncio
from bson import ObjectId
from app.database.mongo import jobs_collection
from app.models.job import JobDB
from app.models.user import Location

async def test_insert_job():
    job = JobDB(
        user_id=ObjectId("6999c820f40ff21361a841eb"),  # Dummy user ID
        input_type="text",
        input_ref="Help required with plumbing",
        skill_required="Plumbing",
        problem="Leaking pipe in kitchen",
        urgency="High",
        location=Location(lat=19.1925, lng=73.1816),
        status="created"
    )

    result = await jobs_collection.insert_one(job.model_dump(by_alias=True))
    print("✅ Inserted Job ID:", result.inserted_id)

if __name__ == "__main__":
    asyncio.run(test_insert_job())

# import asyncio
# from bson import ObjectId
# from app.database.mongo import jobs_collection
# from app.models.job import JobDB
# from app.models.user import Location


# async def seed_jobs():
#     # 🔥 Replace with actual client user ID
#     client_user_id = ObjectId("PUT_CLIENT_USER_ID")

#     jobs = [
#         JobDB(
#             user_id=client_user_id,
#             input_type="voice",
#             input_ref="audio_leak_01.mp3",
#             skill_required="Plumbing",
#             problem="Water leaking under kitchen sink",
#             urgency="High",
#             location=Location(lat=19.2034334, lng=73.18),
#             status="created"
#         ),
#         JobDB(
#             user_id=client_user_id,
#             input_type="text",
#             input_ref="Bathroom tap broken",
#             skill_required="Plumbing",
#             problem="Tap not closing properly",
#             urgency="Low",
#             location=Location(lat=19.2018, lng=73.1812),
#             status="booked"
#         )
#     ]

#     inserted_ids = []

#     for job in jobs:
#         result = await jobs_collection.insert_one(job.model_dump(by_alias=True))
#         inserted_ids.append(result.inserted_id)

#     print("✅ Inserted Jobs:", inserted_ids)


# if __name__ == "__main__":
#     asyncio.run(seed_jobs())