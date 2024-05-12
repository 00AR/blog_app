from collections.abc import Generator

from pymongo import MongoClient

from app.api.deps import get_current_user
from app.config import settings
from app.models.users import AuthUser
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from app.main import app


app.dependency_overrides = {
    get_current_user: lambda: AuthUser(user_id="66408bcd87e2e3971500ce0c")
}

@pytest.fixture(scope="session", autouse=True)
def mongo_db() -> AsyncIOMotorDatabase:
    print("!!!!!!!!", settings.MONGO_DB)
    client = AsyncIOMotorClient(settings.MONGO_DETAILS)
    return client[settings.MONGO_DB]


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_db():
    mongo_client = MongoClient(settings.MONGO_DETAILS)
    if settings.MONGO_DB.startswith("test"):
        mongo_client.drop_database(settings.MONGO_DB)
