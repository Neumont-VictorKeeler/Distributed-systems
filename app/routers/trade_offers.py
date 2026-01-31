from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import TradeOffer, VideoGame, User, TradeOfferStatus
from app.schemas import TradeOfferCreate, TradeOfferResponse, TradeOfferCollection
from app.hateoas import add_trade_offer_links, add_collection_links

router = APIRouter(prefix="/trade-offers", tags=["trade-offers"])


@router.post("", response_model=TradeOfferResponse, status_code=status.HTTP_201_CREATED)
def create_trade_offer(
    trade_offer: TradeOfferCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    offered_game = db.query(VideoGame).filter(VideoGame.id == trade_offer.offered_game_id).first()
    if not offered_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offered game not found"
        )
    
    requested_game = db.query(VideoGame).filter(VideoGame.id == trade_offer.requested_game_id).first()
    if not requested_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested game not found"
        )
    
    if offered_game.id == requested_game.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot trade a game for itself"
        )
    
    if offered_game.owner_id == requested_game.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot trade with yourself"
        )
    
    existing_offer = db.query(TradeOffer).filter(
        TradeOffer.offered_game_id == trade_offer.offered_game_id,
        TradeOffer.requested_game_id == trade_offer.requested_game_id,
        TradeOffer.status == TradeOfferStatus.PENDING
    ).first()
    
    if existing_offer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending trade offer already exists for these games"
        )
    
    db_trade_offer = TradeOffer(
        offered_game_id=trade_offer.offered_game_id,
        requested_game_id=trade_offer.requested_game_id,
        offerer_id=offered_game.owner_id,
        receiver_id=requested_game.owner_id,
        status=TradeOfferStatus.PENDING
    )
    
    db.add(db_trade_offer)
    db.commit()
    db.refresh(db_trade_offer)
    
    response = TradeOfferResponse.model_validate(db_trade_offer)
    response.links = add_trade_offer_links(request, db_trade_offer.id, db_trade_offer.offerer_id, db_trade_offer.receiver_id)
    
    return response


@router.get("/{trade_offer_id}", response_model=TradeOfferResponse)
def get_trade_offer(
    trade_offer_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    trade_offer = db.query(TradeOffer).filter(TradeOffer.id == trade_offer_id).first()
    if not trade_offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade offer not found"
        )
    
    response = TradeOfferResponse.model_validate(trade_offer)
    response.links = add_trade_offer_links(request, trade_offer.id, trade_offer.offerer_id, trade_offer.receiver_id)
    
    return response


@router.get("", response_model=TradeOfferCollection)
def get_all_trade_offers(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    status_filter: TradeOfferStatus = None,
    db: Session = Depends(get_db)
):
    query = db.query(TradeOffer)
    
    if status_filter:
        query = query.filter(TradeOffer.status == status_filter)
    
    trade_offers = query.offset(skip).limit(limit).all()
    
    items = []
    for trade_offer in trade_offers:
        response = TradeOfferResponse.model_validate(trade_offer)
        response.links = add_trade_offer_links(request, trade_offer.id, trade_offer.offerer_id, trade_offer.receiver_id)
        items.append(response)
    
    base_url = str(request.base_url).rstrip('/')
    collection_links = add_collection_links(request, "/trade-offers", skip, limit, len(items))

    return TradeOfferCollection(items=items, links=collection_links)


@router.get("/user/{user_id}/sent", response_model=TradeOfferCollection)
def get_user_sent_offers(
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

    trade_offers = db.query(TradeOffer).filter(
        TradeOffer.offerer_id == user_id
    ).offset(skip).limit(limit).all()

    items = []
    for trade_offer in trade_offers:
        response = TradeOfferResponse.model_validate(trade_offer)
        response.links = add_trade_offer_links(request, trade_offer.id, trade_offer.offerer_id, trade_offer.receiver_id)
        items.append(response)

    base_url = str(request.base_url).rstrip('/')
    collection_links = add_collection_links(request, f"/trade-offers/user/{user_id}/sent", skip, limit, len(items))

    return TradeOfferCollection(items=items, links=collection_links)


@router.get("/user/{user_id}/received", response_model=TradeOfferCollection)
def get_user_received_offers(
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

    trade_offers = db.query(TradeOffer).filter(
        TradeOffer.receiver_id == user_id
    ).offset(skip).limit(limit).all()

    items = []
    for trade_offer in trade_offers:
        response = TradeOfferResponse.model_validate(trade_offer)
        response.links = add_trade_offer_links(request, trade_offer.id, trade_offer.offerer_id, trade_offer.receiver_id)
        items.append(response)

    base_url = str(request.base_url).rstrip('/')
    collection_links = add_collection_links(request, f"/trade-offers/user/{user_id}/received", skip, limit, len(items))

    return TradeOfferCollection(items=items, links=collection_links)


@router.put("/{trade_offer_id}/accept", response_model=TradeOfferResponse)
def accept_trade_offer(
    trade_offer_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    trade_offer = db.query(TradeOffer).filter(TradeOffer.id == trade_offer_id).first()
    if not trade_offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade offer not found"
        )

    if trade_offer.status != TradeOfferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept trade offer with status: {trade_offer.status}"
        )

    trade_offer.status = TradeOfferStatus.ACCEPTED
    db.commit()
    db.refresh(trade_offer)

    response = TradeOfferResponse.model_validate(trade_offer)
    response.links = add_trade_offer_links(request, trade_offer.id, trade_offer.offerer_id, trade_offer.receiver_id)

    return response


@router.put("/{trade_offer_id}/reject", response_model=TradeOfferResponse)
def reject_trade_offer(
    trade_offer_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    trade_offer = db.query(TradeOffer).filter(TradeOffer.id == trade_offer_id).first()
    if not trade_offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade offer not found"
        )

    if trade_offer.status != TradeOfferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject trade offer with status: {trade_offer.status}"
        )

    trade_offer.status = TradeOfferStatus.REJECTED
    db.commit()
    db.refresh(trade_offer)

    response = TradeOfferResponse.model_validate(trade_offer)
    response.links = add_trade_offer_links(request, trade_offer.id, trade_offer.offerer_id, trade_offer.receiver_id)

    return response


@router.put("/{trade_offer_id}/cancel", response_model=TradeOfferResponse)
def cancel_trade_offer(
    trade_offer_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    trade_offer = db.query(TradeOffer).filter(TradeOffer.id == trade_offer_id).first()
    if not trade_offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade offer not found"
        )

    if trade_offer.status != TradeOfferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel trade offer with status: {trade_offer.status}"
        )

    trade_offer.status = TradeOfferStatus.CANCELLED
    db.commit()
    db.refresh(trade_offer)

    response = TradeOfferResponse.model_validate(trade_offer)
    response.links = add_trade_offer_links(request, trade_offer.id, trade_offer.offerer_id, trade_offer.receiver_id)

    return response

