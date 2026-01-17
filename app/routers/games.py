from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, VideoGame
from app.schemas import VideoGameCreate, VideoGameUpdate, VideoGameResponse, VideoGameCollection
from app.hateoas import add_game_links, add_collection_links

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=VideoGameResponse, status_code=status.HTTP_201_CREATED)
def create_game(
    game: VideoGameCreate,
    owner_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner user not found"
        )

    db_game = VideoGame(
        **game.model_dump(),
        owner_id=owner_id
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)

    response = VideoGameResponse.model_validate(db_game)
    response.links = add_game_links(request, db_game.id, owner_id, is_owner=True)

    return response


@router.get("/{game_id}", response_model=VideoGameResponse)
def get_game(
    game_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    game = db.query(VideoGame).filter(VideoGame.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video game not found"
        )

    response = VideoGameResponse.model_validate(game)
    response.links = add_game_links(request, game_id, game.owner_id, is_owner=True)

    return response


@router.get("", response_model=VideoGameCollection)
def get_games(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    games = db.query(VideoGame).offset(skip).limit(limit).all()

    game_responses = []
    for game in games:
        response = VideoGameResponse.model_validate(game)
        response.links = add_game_links(request, game.id, game.owner_id, is_owner=True)
        game_responses.append(response)

    collection = VideoGameCollection(items=game_responses)
    collection.links = add_collection_links(request, "/games")

    return collection


@router.get("/users/{user_id}/games", response_model=VideoGameCollection)
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


@router.put("/{game_id}", response_model=VideoGameResponse)
def update_game(
    game_id: int,
    game_update: VideoGameUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    game = db.query(VideoGame).filter(VideoGame.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video game not found"
        )

    update_data = game_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(game, field, value)

    db.commit()
    db.refresh(game)

    response = VideoGameResponse.model_validate(game)
    response.links = add_game_links(request, game_id, game.owner_id, is_owner=True)

    return response


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(
    game_id: int,
    db: Session = Depends(get_db)
):
    game = db.query(VideoGame).filter(VideoGame.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video game not found"
        )

    db.delete(game)
    db.commit()

    return None

