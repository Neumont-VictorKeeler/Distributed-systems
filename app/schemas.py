from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from app.models import GameCondition, TradeOfferStatus
from datetime import datetime


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    street_address: str = Field(..., min_length=1, max_length=200)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    street_address: Optional[str] = Field(None, min_length=1, max_length=200)


class UserResponse(UserBase):
    id: int
    links: Dict[str, Any] = {}
    
    model_config = ConfigDict(from_attributes=True)


class VideoGameBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    publisher: str = Field(..., min_length=1, max_length=100)
    year_published: int = Field(..., ge=1950, le=2100)
    gaming_system: str = Field(..., min_length=1, max_length=100)
    condition: GameCondition
    previous_owners: Optional[int] = Field(None, ge=0)


class VideoGameCreate(VideoGameBase):
    pass


class VideoGameUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    publisher: Optional[str] = Field(None, min_length=1, max_length=100)
    year_published: Optional[int] = Field(None, ge=1950, le=2100)
    gaming_system: Optional[str] = Field(None, min_length=1, max_length=100)
    condition: Optional[GameCondition] = None
    previous_owners: Optional[int] = Field(None, ge=0)


class VideoGameResponse(VideoGameBase):
    id: int
    owner_id: int
    links: Dict[str, Any] = {}
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
    links: Dict[str, Any] = {}


class TokenData(BaseModel):
    email: Optional[str] = None


class VideoGameCollection(BaseModel):
    items: List[VideoGameResponse]
    links: Dict[str, Any] = {}


class UserCollection(BaseModel):
    items: List[UserResponse]
    links: Dict[str, Any] = {}


class TradeOfferBase(BaseModel):
    offered_game_id: int
    requested_game_id: int


class TradeOfferCreate(TradeOfferBase):
    pass


class TradeOfferResponse(TradeOfferBase):
    id: int
    offerer_id: int
    receiver_id: int
    status: TradeOfferStatus
    created_at: datetime
    updated_at: datetime
    links: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class TradeOfferCollection(BaseModel):
    items: List[TradeOfferResponse]
    links: Dict[str, Any] = {}


class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int

