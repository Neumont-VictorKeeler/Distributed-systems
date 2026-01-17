from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, VideoGame
from app.schemas import UserCreate, UserUpdate, UserResponse, UserCollection, VideoGameResponse, VideoGameCollection
from app.hateoas import add_user_links, add_collection_links, add_game_links

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=user.password,
        street_address=user.street_address
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    response = UserResponse.model_validate(db_user)
    response.links = add_user_links(request, db_user.id, is_owner=True)

    return response


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    response = UserResponse.model_validate(user)
    response.links = add_user_links(request, user_id, is_owner=True)

    return response


@router.get("", response_model=UserCollection)
def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()

    user_responses = []
    for user in users:
        response = UserResponse.model_validate(user)
        response.links = add_user_links(request, user.id, is_owner=True)
        user_responses.append(response)

    collection = UserCollection(items=user_responses)
    collection.links = add_collection_links(request, "/users")

    return collection


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    response = UserResponse.model_validate(user)
    response.links = add_user_links(request, user_id, is_owner=True)

    return response


@router.get("/{user_id}/games", response_model=VideoGameCollection)
def get_user_games(
    user_id: int,
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    games = db.query(VideoGame).filter(VideoGame.owner_id == user_id).offset(skip).limit(limit).all()

    game_responses = []
    for game in games:
        response = VideoGameResponse.model_validate(game)
        response.links = add_game_links(request, game.id, game.owner_id, is_owner=True)
        game_responses.append(response)

    collection = VideoGameCollection(items=game_responses)
    collection.links = add_collection_links(request, f"/users/{user_id}/games")

    return collection

