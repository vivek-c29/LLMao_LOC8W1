import asyncio
from bson import ObjectId
from app.database.mongo import users_collection
from app.models.user import UserDB, Location


async def test_insert():
    user = UserDB(
        name="Omkar",
        phone="9815847362",
        role="user",
        language="en",
        location=Location(lat=19.2035, lng=73.18),
    )

    result = await users_collection.insert_one(user.model_dump(by_alias=True))
    print("✅ Inserted User ID:", result.inserted_id)


if __name__ == "__main__":
    asyncio.run(test_insert())

# import asyncio
# from app.database.mongo import users_collection
# from app.models.user import UserDB, Location


# async def seed_users():
#     users = [
#         # Clients
#         UserDB(
#             name="Rahul Sharma",
#             phone="9024224421",
#             role="user",
#             language="hi",
#             location=Location(lat=19.2035, lng=73.1799),
#         ),
#         UserDB(
#             name="Sneha Patil",
#             phone="9213400002",
#             role="user",
#             language="mr",
#             location=Location(lat=19.2018, lng=73.1812),
#         ),

#         # Worker Auth Accounts
#         UserDB(
#             name="Ramesh Yadav",
#             phone="9123456783",
#             role="worker",
#             language="hi",
#             location=Location(lat=19.2050, lng=73.1810),
#         ),
#         UserDB(
#             name="Suresh Naik",
#             phone="887722334",
#             role="worker",
#             language="mr",
#             location=Location(lat=19.1985, lng=73.1760),
#         ),
#         UserDB(
#             name="Imran Shaikh",
#             phone="9876543215",
#             role="worker",
#             language="hi",
#             location=Location(lat=19.2150, lng=73.1900),
#         ),
#     ]

#     inserted_ids = []

#     for user in users:
#         result = await users_collection.insert_one(user.model_dump(by_alias=True))
#         inserted_ids.append(result.inserted_id)

#     print("✅ Inserted Users:", inserted_ids)


# if __name__ == "__main__":
#     asyncio.run(seed_users())