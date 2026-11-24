from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import current_user, require_family, require_provider
from app.models import (
    Block,
    ConnectionRequest,
    Conversation,
    FamilyProfile,
    Message,
    Notification,
    Provider,
    Recipient,
    Review,
    User,
)
from app.trust import recompute

router = APIRouter(tags=["care"])


class RequestIn(BaseModel):
    provider_id: int
    recipient_id: int
    service: str
    include_health: bool = False


class MessageIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class OutcomeIn(BaseModel):
    met_need: bool


class ReviewIn(BaseModel):
    provider_id: int
    rating: int = Field(ge=1, le=5)
    body: str = Field(default="", max_length=2000)
    alias: str = Field(min_length=2, max_length=80)


def _notify(db: Session, user_id: int, title: str, body: str) -> None:
    db.add(Notification(user_id=user_id, title=title, body=body))


@router.post("/requests")
def create_request(body: RequestIn, ctx: tuple[User, FamilyProfile] = Depends(require_family), db: Session = Depends(get_db)):
    user, family = ctx
    recipient = db.get(Recipient, body.recipient_id)
    provider = db.get(Provider, body.provider_id)
    if recipient is None or recipient.family_id != family.id or recipient.archived:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if provider is None or provider.registration_status != "approved" or provider.user.status != "active":
        raise HTTPException(status_code=400, detail="That provider cannot receive a new request")
    if provider.accepting == "not_accepting":
        raise HTTPException(status_code=400, detail="That provider is not accepting new requests")
    blocked = (
        db.query(Block).filter(Block.family_id == family.id, Block.provider_id == provider.id).one_or_none()
    )
    if blocked:
        raise HTTPException(status_code=400, detail="New requests are blocked for this pair")
    open_request = (
        db.query(ConnectionRequest)
        .filter(
            ConnectionRequest.family_id == family.id,
            ConnectionRequest.provider_id == provider.id,
            ConnectionRequest.recipient_id == recipient.id,
            ConnectionRequest.service == body.service,
            ConnectionRequest.status.in_(["pending", "accepted"]),
        )
        .one_or_none()
    )
    if open_request:
        return _request_out(open_request, provider, recipient)

    diagnosis = recipient.diagnosis if body.include_health else "not included"
    needs = recipient.needs if body.include_health else ""
    disclosure = f"{recipient.alias}, age {recipient.age}. Service: {body.service}. Diagnosis: {diagnosis}."
    if needs:
        disclosure = f"{disclosure} Needs: {needs}"
    row = ConnectionRequest(
        family_id=family.id,
        provider_id=provider.id,
        recipient_id=recipient.id,
        service=body.service,
        disclosure=disclosure,
        include_health=body.include_health,
    )
    db.add(row)
    conversation = (
        db.query(Conversation)
        .filter(Conversation.family_id == family.id, Conversation.provider_id == provider.id)
        .one_or_none()
    )
    if conversation is None:
        db.add(Conversation(family_id=family.id, provider_id=provider.id))
    _notify(db, provider.user_id, "New connection request", "A family sent a connection request. Open Requests to respond.")
    db.commit()
    db.refresh(row)
    return _request_out(row, provider, recipient)


@router.get("/requests")
def list_requests(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = db.query(ConnectionRequest)
    if user.role == "family":
        query = query.filter(ConnectionRequest.family_id == user.family.id)
    elif user.role == "provider":
        query = query.filter(ConnectionRequest.provider_id == user.provider.id)
    else:
        raise HTTPException(status_code=403, detail="Family or provider account required")
    rows = query.order_by(ConnectionRequest.created_at.desc()).all()
    return {"results": [_request_row(db, row) for row in rows]}


@router.post("/requests/{request_id}/accept")
def accept_request(request_id: int, ctx: tuple[User, Provider] = Depends(require_provider), db: Session = Depends(get_db)):
    return _decide(request_id, "accepted", ctx[1], db)


@router.post("/requests/{request_id}/decline")
def decline_request(request_id: int, ctx: tuple[User, Provider] = Depends(require_provider), db: Session = Depends(get_db)):
    return _decide(request_id, "declined", ctx[1], db)


@router.post("/requests/{request_id}/outcome")
def record_outcome(
    request_id: int,
    body: OutcomeIn,
    ctx: tuple[User, FamilyProfile] = Depends(require_family),
    db: Session = Depends(get_db),
):
    _, family = ctx
    row = db.get(ConnectionRequest, request_id)
    if row is None or row.family_id != family.id:
        raise HTTPException(status_code=404, detail="Request not found")
    if row.status not in {"accepted", "completed"}:
        raise HTTPException(status_code=400, detail="Confirm service only after the provider accepts")
    row.status = "completed"
    row.met_need = body.met_need
    row.completed_at = row.completed_at or datetime.utcnow()
    provider = db.get(Provider, row.provider_id)
    if provider:
        recompute(db, provider)
    db.commit()
    return _request_row(db, row)


def _decide(request_id: int, status: str, provider: Provider, db: Session) -> dict:
    row = db.get(ConnectionRequest, request_id)
    if row is None or row.provider_id != provider.id:
        raise HTTPException(status_code=404, detail="Request not found")
    if row.status != "pending":
        return _request_row(db, row)
    row.status = status
    family = db.get(FamilyProfile, row.family_id)
    if family:
        _notify(db, family.user_id, "Request updated", f"A provider {status} a connection request.")
    db.commit()
    return _request_row(db, row)


@router.get("/conversations")
def conversations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = db.query(Conversation)
    if user.role == "family":
        query = query.filter(Conversation.family_id == user.family.id)
    elif user.role == "provider":
        query = query.filter(Conversation.provider_id == user.provider.id)
    else:
        raise HTTPException(status_code=403, detail="Family or provider account required")
    results = []
    for row in query.all():
        provider = db.get(Provider, row.provider_id)
        family = db.get(FamilyProfile, row.family_id)
        results.append(
            {
                "id": row.id,
                "provider_name": provider.display_name if provider else "Provider",
                "family_name": family.user.name if family else "Family",
            }
        )
    return {"results": results}


@router.get("/conversations/{conversation_id}/messages")
def messages(conversation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = _conversation_for(user, db, conversation_id)
    items = db.query(Message).filter(Message.conversation_id == row.id).order_by(Message.created_at.asc()).all()
    return {
        "results": [
            {"id": item.id, "body": item.body, "mine": item.sender_user_id == user.id, "created_at": item.created_at.isoformat()}
            for item in items
        ]
    }


@router.post("/conversations/{conversation_id}/messages")
def send_message(
    conversation_id: int,
    body: MessageIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    row = _conversation_for(user, db, conversation_id)
    if user.status != "active":
        raise HTTPException(status_code=403, detail="Suspended accounts cannot send messages")
    blocked = db.query(Block).filter(Block.family_id == row.family_id, Block.provider_id == row.provider_id).one_or_none()
    if blocked:
        raise HTTPException(status_code=400, detail="Messaging is blocked for this pair")
    message = Message(conversation_id=row.id, sender_user_id=user.id, body=body.body.strip())
    db.add(message)
    other_id = _other_user_id(db, row, user)
    _notify(db, other_id, "New message", "You have a new message. Open Messages to read it.")
    provider = db.get(Provider, row.provider_id)
    db.commit()
    if provider:
        recompute(db, provider)
        db.commit()
    db.refresh(message)
    return {"id": message.id, "body": message.body, "mine": True, "created_at": message.created_at.isoformat()}


@router.post("/reviews")
def submit_review(body: ReviewIn, ctx: tuple[User, FamilyProfile] = Depends(require_family), db: Session = Depends(get_db)):
    _, family = ctx
    eligible = (
        db.query(ConnectionRequest)
        .filter(
            ConnectionRequest.family_id == family.id,
            ConnectionRequest.provider_id == body.provider_id,
            ConnectionRequest.status == "completed",
        )
        .first()
    )
    if eligible is None:
        raise HTTPException(status_code=400, detail="A review opens after you confirm that service was received")
    existing = db.query(Review).filter(Review.family_id == family.id, Review.provider_id == body.provider_id).one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="This family already reviewed that provider")
    review = Review(
        family_id=family.id,
        provider_id=body.provider_id,
        rating=body.rating,
        body=body.body.strip(),
        alias=body.alias.strip(),
        status="pending",
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"id": review.id, "status": review.status}


def _conversation_for(user: User, db: Session, conversation_id: int) -> Conversation:
    row = db.get(Conversation, conversation_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if user.role == "family" and user.family and row.family_id == user.family.id:
        return row
    if user.role == "provider" and user.provider and row.provider_id == user.provider.id:
        return row
    raise HTTPException(status_code=403, detail="You cannot open this conversation")


def _other_user_id(db: Session, row: Conversation, user: User) -> int:
    if user.role == "family":
        provider = db.get(Provider, row.provider_id)
        return provider.user_id
    family = db.get(FamilyProfile, row.family_id)
    return family.user_id


def _request_row(db: Session, row: ConnectionRequest) -> dict:
    provider = db.get(Provider, row.provider_id)
    recipient = db.get(Recipient, row.recipient_id)
    return _request_out(row, provider, recipient)


def _request_out(row: ConnectionRequest, provider: Provider | None, recipient: Recipient | None) -> dict:
    return {
        "id": row.id,
        "provider_id": row.provider_id,
        "provider_name": provider.display_name if provider else "Provider",
        "recipient_alias": recipient.alias if recipient else "Recipient",
        "service": row.service,
        "status": row.status,
        "disclosure": row.disclosure,
        "include_health": row.include_health,
        "met_need": row.met_need,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
