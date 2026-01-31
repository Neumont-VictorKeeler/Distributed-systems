from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime


class GameCondition(str, enum.Enum):
    MINT = "mint"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class TradeOfferStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


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
    offered_trades = relationship("TradeOffer", foreign_keys="TradeOffer.offered_game_id", back_populates="offered_game")
    requested_trades = relationship("TradeOffer", foreign_keys="TradeOffer.requested_game_id", back_populates="requested_game")


class TradeOffer(Base):
    __tablename__ = "trade_offers"

    id = Column(Integer, primary_key=True, index=True)
    offered_game_id = Column(Integer, ForeignKey("video_games.id"), nullable=False)
    requested_game_id = Column(Integer, ForeignKey("video_games.id"), nullable=False)
    offerer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(TradeOfferStatus), nullable=False, default=TradeOfferStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    offered_game = relationship("VideoGame", foreign_keys=[offered_game_id], back_populates="offered_trades")
    requested_game = relationship("VideoGame", foreign_keys=[requested_game_id], back_populates="requested_trades")
    offerer = relationship("User", foreign_keys=[offerer_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

