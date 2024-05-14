from pydantic import BaseModel, EmailStr, Field

class UserSchema(BaseModel):
    name: str
    email: EmailStr
    password: str


class AuthUser(BaseModel):
    user_id: str


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)