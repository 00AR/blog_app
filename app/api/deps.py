from app.auth.auth_handler import decode_jwt
from app.config import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


async def get_current_user(token):
    decoded_token = decode_jwt(token)
    mongo_db = await get_mongo()
    user_id = await mongo_db.users.find_one({ "email": decoded_token["user_id"] })
    return user_id["name"]


async def get_mongo() -> AsyncIOMotorDatabase:
    ip = settings.MONGO_IP
    port = settings.MONGO_PORT
    username = settings.MONGO_USER
    pwd = settings.MONGO_PWD
    mongo_uri = "mongodb://" + str(ip) + ":" + str(port) + username + pwd

    client = AsyncIOMotorClient(mongo_uri)
    return client[settings.MONGO_DB]
