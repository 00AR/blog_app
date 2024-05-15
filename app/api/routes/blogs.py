from datetime import datetime
from typing import Annotated, Any
from bson import ObjectId
from fastapi import Path
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_mongo
from app.auth.auth_bearer import JWTBearer
from app.models.blogs import AddCommentSchema, BlogDetailResponseSchema, BlogSchema, CreateBlogSchema, ReactionTypeEnum, UserReactionSchema
from app.models.users import AuthUser


router = APIRouter()

id_regex = r"^[0-9a-f]{24}$"


@router.post("/")
async def create_blog(
    blog: CreateBlogSchema,
    token: Annotated[str, Depends(JWTBearer())],
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    """
    Create new blog.
    """
    # TODO: is it ok to not check token of being None
    username = await get_current_user(token)
    insert_blog = BlogSchema(
        title=blog.title,
        content=blog.content,
        created_by=username,
    )
    blog_dict = dict(insert_blog)
    await mongo_db.blogs.insert_one(blog_dict)
    blog_dict["_id"] = str(blog_dict["_id"])
    return blog_dict


@router.put("/{blog_id}")
async def update_blog(
    blog: CreateBlogSchema,
    token: Annotated[str, Depends(JWTBearer())],
    blog_id: str = Path(..., pattern=id_regex),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    username = await get_current_user(token)
    blog_id = ObjectId(blog_id)
    document = await mongo_db.blogs.find_one({"_id": blog_id})
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blog with given id does not exists!",
        )
    if username != document["created_by"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this blog",
        )
    mongo_db.blogs.update_one(
        {"_id": blog_id}, 
        {
            "$set": {
                "title": blog.title,
                "content": blog.content
            }
        }
    )
    document["title"] = blog.title
    document["content"] = blog.content
    document["_id"] = str(document["_id"])
    return document


@router.delete("/{blog_id}", status_code=204)
async def delete_blog(
    blog_id: str = Path(..., pattern=id_regex),
    user: AuthUser = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    blog_id = ObjectId(blog_id)
    document = await mongo_db.blogs.find_one({"_id": blog_id})
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blog with given id does not exists!",
        )
    if user.user_id != document["created_by"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this blog",
        )
    await mongo_db.blogs.delete_one({"_id": blog_id})
    await mongo_db.reactions.delete_many({"blog_id": blog_id})
    await mongo_db.comments.delete_many({"blog_id": blog_id})
    return {"message": "document deleted successfully!"}


@router.get("/")
async def get_blogs(
    created_by: str = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    skip = (page - 1) * per_page
    filter_query = {}
    if created_by is not None:
        filter_query["created_by"] = created_by
    cursor = (
        mongo_db.blogs.find(
            filter_query,
            {'content': False}
        )
        .sort({"created_at": -1})
        .skip(skip)
        .limit(per_page)
    )
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    total_count = await mongo_db.blogs.count_documents(filter_query)
    total_pages = (total_count // per_page) + int(total_count%per_page)
    pagination = {"page": page, "per_page": per_page, "total_pages": total_pages, "total_count": total_count}
    return {
        "data": results,
        "pagination": pagination
    }


@router.get("/{blog_id}", response_model=BlogDetailResponseSchema)
async def get_blog_detail(
    blog_id: str = Path(..., pattern=id_regex),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    blog_id = ObjectId(blog_id)
    document = await mongo_db.blogs.find_one({"_id": blog_id})
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blog with given id does not exists!",
        )
    document["_id"] = str(document["_id"])
    return document


@router.post("/{blog_id}/comments")
async def add_comment(
    data: AddCommentSchema,
    blog_id: str = Path(..., pattern=id_regex),
    token: Annotated[str, Depends(JWTBearer())] = None,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    username = await get_current_user(token)
    blog_id = ObjectId(blog_id)
    blog = await mongo_db.blogs.find_one({"_id": blog_id}, {"_id": True})
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blog with given id does not exists!",
        )
    user_comment = {
        "user_id": username,
        "blog_id": blog_id,
        "comment": data.comment,
        "created_at": datetime.now()
    }
    await mongo_db.blogs.update_one(
        {"_id": blog_id},
        {"$inc": {"comments": 1}}
    )
    await mongo_db.comments.insert_one(user_comment)
    user_comment["_id"] = str(user_comment["_id"])
    user_comment["blog_id"] = str(user_comment["blog_id"])
    user_comment["user_id"] = str(user_comment["user_id"])
    return user_comment


@router.delete("/{blog_id}/comments/{comment_id}", status_code=204)
async def delete_comment(
    blog_id: str = Path(..., pattern=id_regex),
    comment_id: str = Path(..., pattern=id_regex),
    user: AuthUser = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    comment_id = ObjectId(comment_id)
    user_comment = await mongo_db.comments.find_one({"_id": comment_id})
    if user_comment is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No such comment.",
        )
    if user_comment["user_id"] != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorized to delete this comment",
        )
    await mongo_db.blogs.update_one(
        {"_id": blog_id},
        {"$inc": {"comments": -1}}
    )
    await mongo_db.comments.delete_one({"_id": comment_id})
    return {"message": "comment deleted successfully"}


@router.put("/{blog_id}/comments/{comment_id}")
async def update_comment(
    data: AddCommentSchema,
    comment_id: str = Path(..., pattern=id_regex),
    user: AuthUser = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    comment_id = ObjectId(comment_id)
    user_comment = await mongo_db.comments.find_one({"_id": comment_id})
    if user_comment is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No such comment.",
        )
    if user_comment["user_id"] != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot update this comment.",
        )
    await mongo_db.comments.update_one(
        {"_id": comment_id}, 
        {
            "$set": {
                "comment": data.comment
            }
        }
    )
    user_comment["_id"] = str(user_comment["_id"])
    user_comment["user_id"] = str(user_comment["user_id"])
    user_comment["blog_id"] = str(user_comment["blog_id"])
    return user_comment


@router.get("/{blog_id}/comments")
async def get_blog_comments(
    blog_id: str = Path(..., pattern=id_regex),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    blog_id = ObjectId(blog_id)
    blog = await mongo_db.blogs.find_one({"_id": blog_id}, {"_id": True})
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blog with given id does not exists!",
        )
    skip = (page - 1) * per_page
    cursor = (
        mongo_db.comments.find()
        .sort({"created_at": -1})
        .skip(skip)
        .limit(per_page)
    )
    all_comments = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"]);
        doc["user_id"] = str(doc["user_id"])
        doc["blog_id"] = str(doc["blog_id"])
        all_comments.append(doc)
    return all_comments


@router.post("/{blog_id}/{reaction_type}", response_model=UserReactionSchema)
async def reaction(
    reaction_type: ReactionTypeEnum,
    blog_id: str = Path(..., pattern=id_regex),
    user: AuthUser = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    blog_id = ObjectId(blog_id)
    blog = await mongo_db.blogs.find_one({"_id": blog_id}, {"_id": True})
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blog with given id does not exists!",
        )
    user_reaction = await mongo_db.user_reactions.find_one({"blog_id": blog_id, "user_id": user.user_id})
    if user_reaction is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reacted. Please undo reaction and try again.",
        )
    user_reaction = {
        "user_id": user.user_id,
        "blog_id": blog_id,
        "reaction_type": reaction_type,
    }
    await mongo_db.user_reactions.insert_one(user_reaction)
    await mongo_db.blogs.update_one(
        {"_id": blog_id},
        {"$inc": {reaction_type: 1}}
    )
    user_reaction["user_id"] = str(user_reaction["user_id"])
    user_reaction["blog_id"] = str(user_reaction["blog_id"])
    return user_reaction


@router.delete("/{blog_id}/{reaction_type}", status_code=204)
async def undo_reaction(
    reaction_type: ReactionTypeEnum,
    blog_id: str = Path(..., pattern=id_regex),
    user: AuthUser = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo),
):
    blog_id = ObjectId(blog_id)
    user_reaction = await mongo_db.user_reactions.find_one({"blog_id": blog_id, "user_id": user.user_id, "reaction_type": reaction_type})
    if user_reaction is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not reacted yet.",
        )
    await mongo_db.user_reactions.delete_one({"_id": user_reaction["_id"]})
    await mongo_db.blogs.update_one(
        {"_id": blog_id},
        {"$inc": {reaction_type: -1}}
    )
    return {"message": "You have undone the reaction!"}