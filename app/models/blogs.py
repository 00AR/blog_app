from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class ReactionTypeEnum(str, Enum):
    likes = "likes"
    dislikes = "dislikes"


class CreateBlogSchema(BaseModel):
    title: str
    content: str


class BlogSchema(BaseModel):
    title: str
    content: str
    likes: int = 0
    dislikes: int = 0
    comments: int = 0
    created_at: datetime = datetime.now()
    created_by: str


class BlogDetailResponseSchema(BlogSchema):
    _id: str


class UserReactionSchema(BaseModel):
    user_id: str
    blog_id: str
    reaction_type: ReactionTypeEnum


class AddCommentSchema(BaseModel):
    comment: str

