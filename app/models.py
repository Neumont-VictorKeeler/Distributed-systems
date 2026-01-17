from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class GameCondition(str, enum.Enum):
    MINT = "mint"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    street_address = Column(String, nullable=False)

    video_games = relationship("VideoGame", back_populates="owner", cascade="all, delete-orphan")


class VideoGame(Base):
    __tablename__ = "video_games"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    publisher = Column(String, nullable=False)
    year_published = Column(Integer, nullable=False)
    gaming_system = Column(String, nullable=False)
    condition = Column(SQLEnum(GameCondition), nullable=False)
    previous_owners = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="video_games")

