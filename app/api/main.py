from fastapi import APIRouter

from app.api.routes import users, blogs

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(blogs.router, prefix="/blogs", tags=["blogs"])