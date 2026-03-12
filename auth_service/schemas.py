from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)


class UserResponse(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    id: int
    hashed_password: str
    
    model_config = ConfigDict(from_attributes=True)

