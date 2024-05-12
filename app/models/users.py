from pydantic import BaseModel

class UserSchema(BaseModel):
    name: str
    email: str
    password: str


class AuthUser(BaseModel):
    user_id: str