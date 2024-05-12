from app.config import settings
from app.models.users import AuthUser
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


async def get_current_user():
    return AuthUser(user_id="test-user")


async def get_mongo() -> AsyncIOMotorDatabase:
    ip = settings.MONGO_IP
    port = settings.MONGO_PORT
    username = settings.MONGO_USER
    pwd = settings.MONGO_PWD
    mongo_uri = "mongodb://" + str(ip) + ":" + str(port) + username + pwd

    client = AsyncIOMotorClient(mongo_uri)
    return client[settings.MONGO_DB]
