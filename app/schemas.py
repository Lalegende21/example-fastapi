from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint


class User(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    description: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    # owner_id: int
    owner: UserOut
    class Config:
        from_attributes = True


class PostOut(BaseModel):
    Post: Post
    votes: int
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: int = conint(le=1)()  # 1 means like, 0 means unlike