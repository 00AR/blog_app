from fastapi import FastAPI, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_mongo
from app.auth.auth_handler import sign_jwt
from app.models.users import UserSchema, UserLoginSchema
from app.auth.hashing import get_password_hash


router = APIRouter()


@router.post("/user/signup", tags=["users"])
async def create_user(
    user: UserSchema,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    user_exists = await mongo_db.users.find_one({ "email": user.email })
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists!",
        )
    user.password = get_password_hash(user.password)
    mongo_db.users.insert_one({
        "name": user.name,
        "email": user.email,
        "password": user.password
    })
    return sign_jwt(user.email)


@router.post("/user/login", tags=["users"])
async def user_login(
    user: UserLoginSchema,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    # check if the user is registered
    is_registered = await mongo_db.users.find_one({ "email": user.email })
    if is_registered:
        return sign_jwt(user.email)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email/password"
    )