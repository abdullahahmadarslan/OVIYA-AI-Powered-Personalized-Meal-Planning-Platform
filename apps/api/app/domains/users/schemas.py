from pydantic import BaseModel, EmailStr
from typing import List, Literal

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    sex: Literal["male", "female", "other"]
    activity_level: Literal["sedentary", "light", "moderate", "active", "very active"]
    goals: Literal["loss", "gain", "maintenance"]
    dietary_preference: Literal["vegan", "keto", "halal", "none"]
    disliked_ingredients: List[str]
    allergies: List[str]
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True  # ORM mode

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None
