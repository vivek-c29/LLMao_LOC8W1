import asyncio
from bson import ObjectId
from app.database.mongo import workers_collection
from app.models.worker import WorkerDB
from app.models.user import Location

async def test_insert_worker():
    worker = WorkerDB(
        user_id=ObjectId("6999c820f40ff21361a841eb"),  # Dummy user ID
        skills=["Plumbing", "Electrical"],
        experience_years=5,
        availability=True,
        verified=True,
        rating=4.5,
        total_jobs=10,
        location=Location(lat=19.2, lng=73.18)
    )

    result = await workers_collection.insert_one(worker.model_dump(by_alias=True))
    print("✅ Inserted Worker ID:", result.inserted_id)

if __name__ == "__main__":
    asyncio.run(test_insert_worker())


# import asyncio
# from bson import ObjectId
# from app.database.mongo import workers_collection
# from app.models.worker import WorkerDB
# from app.models.user import Location


# async def seed_workers():
#     # 🔥 Replace these with actual worker user IDs from DB
#     worker_user_ids = [
#         ObjectId("6999c6ffbee63270fd3bd6b4"),
#         ObjectId("6999c6ffbee63270fd3bd6b3"),
#         ObjectId("6999c6ffbee63270fd3bd6b2"),
#     ]

#     workers = [
#         WorkerDB(
#             user_id=worker_user_ids[0],
#             skills=["Plumbing"],
#             experience_years=8,
#             availability=True,
#             verified=True,
#             rating=4.8,
#             total_jobs=54,
#             location=Location(lat=19.2050, lng=73.1810)
#         ),
#         WorkerDB(
#             user_id=worker_user_ids[1],
#             skills=["Plumbing"],
#             experience_years=5,
#             availability=True,
#             verified=True,
#             rating=4.3,
#             total_jobs=31,
#             location=Location(lat=19.1985, lng=73.1760)
#         ),
#         WorkerDB(
#             user_id=worker_user_ids[2],
#             skills=["Plumbing"],
#             experience_years=3,
#             availability=False,
#             verified=False,
#             rating=3.9,
#             total_jobs=18,
#             location=Location(lat=19.2150, lng=73.1900)
#         ),
#     ]

#     inserted_ids = []

#     for worker in workers:
#         result = await workers_collection.insert_one(worker.model_dump(by_alias=True))
#         inserted_ids.append(result.inserted_id)

#     print("✅ Inserted Workers:", inserted_ids)


# if __name__ == "__main__":
#     asyncio.run(seed_workers())