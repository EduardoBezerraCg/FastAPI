from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List


##########################   Social Media Post part    #######################################
class Post(BaseModel):
    title: str
    content: str
    published: bool = True

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id : int
    created_at: datetime

    class Config:
        from_attributes = True


##########################   User part    #######################################
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool 
    created_at: datetime

    class Config:
        from_attributes = True