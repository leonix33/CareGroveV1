from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin
from app.models import AuditEvent, ConnectionRequest, Evidence, Provider, Review, User
from app.trust import recompute

router = APIRouter(prefix="/admin", tags=["admin"])


class DecisionIn(BaseModel):
    status: str
    reason: str = ""


class EvidenceDecision(BaseModel):
    status: str
    note: str = ""


@router.get("/overview")
def overview(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    _ = user
    requests = db.query(ConnectionRequest).all()
    counts = {"pending": 0, "accepted": 0, "declined": 0, "completed": 0}
    for row in requests:
        counts[row.status] = counts.get(row.status, 0) + 1
    return {
        "families": db.query(User).filter(User.role == "family", User.status == "active").count(),
        "providers": db.query(User).filter(User.role == "provider", User.status == "active").count(),
        "approved_providers": db.query(Provider).filter(Provider.registration_status == "approved").count(),
        "verified_providers": db.query(Provider).filter(Provider.score_state == "published").count(),
        "requests": counts,
    }


@router.get("/providers")
def providers(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(Provider).all()
    return {
        "results": [
            {
                "id": row.id,
                "display_name": row.display_name,
                "registration_status": row.registration_status,
                "membership": row.membership,
                "payment_status": row.payment_status,
                "paid_through": row.paid_through.isoformat() if row.paid_through else None,
                "score": row.score_value,
                "score_state": row.score_state,
                "email": row.user.email,
            }
            for row in rows
        ]
    }


@router.post("/providers/{provider_id}/registration")
def decide_registration(
    provider_id: int,
    body: DecisionIn,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if body.status not in {"approved", "rejected", "pending"}:
        raise HTTPException(status_code=400, detail="Unknown registration status")
    provider = _provider(db, provider_id)
    provider.registration_status = body.status
    if body.status == "approved":
        provider.approved_at = provider.approved_at or datetime.utcnow()
    _audit(db, actor, "registration_decision", provider.id, body.reason or body.status)
    recompute(db, provider)
    db.commit()
    return {"id": provider.id, "registration_status": provider.registration_status, "score_state": provider.score_state}


@router.get("/evidence")
def evidence(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(Evidence).all()
    return {
        "results": [
            {
                "id": row.id,
                "provider_id": row.provider_id,
                "provider_name": row.provider.display_name,
                "category": row.category,
                "subject": row.subject,
                "status": row.status,
                "expires_on": row.expires_on.isoformat() if row.expires_on else None,
                "file_name": row.file_name,
                "note": row.note,
            }
            for row in rows
        ]
    }


@router.post("/evidence/{evidence_id}")
def decide_evidence(
    evidence_id: int,
    body: EvidenceDecision,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if body.status not in {"verified", "rejected", "not_applicable", "submitted"}:
        raise HTTPException(status_code=400, detail="Unknown evidence status")
    row = db.get(Evidence, evidence_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Evidence not found")
    row.status = body.status
    row.note = body.note
    _audit(db, actor, "evidence_decision", row.id, body.note or body.status)
    recompute(db, row.provider)
    db.commit()
    return {"id": row.id, "status": row.status, "score_state": row.provider.score_state}


@router.get("/reviews")
def reviews(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(Review).order_by(Review.created_at.desc()).all()
    return {
        "results": [
            {
                "id": row.id,
                "provider_id": row.provider_id,
                "provider_name": row.provider.display_name,
                "alias": row.alias,
                "rating": row.rating,
                "body": row.body,
                "status": row.status,
                "decision_reason": row.decision_reason,
            }
            for row in rows
        ]
    }


@router.post("/reviews/{review_id}")
def decide_review(review_id: int, body: DecisionIn, actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    if body.status not in {"published", "rejected", "removed"}:
        raise HTTPException(status_code=400, detail="Unknown review status")
    row = db.get(Review, review_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Review not found")
    row.status = body.status
    row.decision_reason = body.reason
    _audit(db, actor, "review_decision", row.id, body.reason or body.status)
    recompute(db, row.provider)
    db.commit()
    return {"id": row.id, "status": row.status}


def _provider(db: Session, provider_id: int) -> Provider:
    provider = db.get(Provider, provider_id)
    if provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


def _audit(db: Session, actor: User, action: str, record_id: int, reason: str) -> None:
    db.add(
        AuditEvent(
            actor_id=actor.id,
            action=action,
            record_type=action.split("_")[0],
            record_id=str(record_id),
            reason=reason,
        )
    )
