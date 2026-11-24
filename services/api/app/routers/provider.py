from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.deps import require_provider
from app.models import AuditEvent, Evidence, Provider, Review, User
from app.present import provider_self
from app.trust import recompute

router = APIRouter(prefix="/provider", tags=["provider"])


class ProfileIn(BaseModel):
    legal_name: str = ""
    display_name: str
    provider_type: str = ""
    description: str = ""
    zip_code: str = ""
    state: str = ""
    services: list[str] = []
    diagnoses: list[str] = []
    age_min: int | None = None
    age_max: int | None = None
    specialties: list[str] = []
    coverage_programs: list[str] = []
    coverage_states: list[str] = []
    accepting: str = "not_specified"
    capacity: int | None = Field(default=None, ge=0)
    experience_years: int | None = Field(default=None, ge=0)
    qualifications: str = ""


class EvidenceIn(BaseModel):
    category: str
    subject: str = "company"
    file_name: str
    expires_on: date | None = None


@router.get("/profile")
def profile(ctx: tuple[User, Provider] = Depends(require_provider)):
    return provider_self(ctx[1])


@router.put("/profile")
def update_profile(body: ProfileIn, ctx: tuple[User, Provider] = Depends(require_provider), db: Session = Depends(get_db)):
    _, provider = ctx
    for key, value in body.model_dump().items():
        setattr(provider, key, value)
    recompute(db, provider)
    db.commit()
    return provider_self(provider)


@router.post("/evidence")
def add_evidence(body: EvidenceIn, ctx: tuple[User, Provider] = Depends(require_provider), db: Session = Depends(get_db)):
    _, provider = ctx
    if not body.file_name.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Upload a PDF, JPG, or PNG")
    row = Evidence(
        provider_id=provider.id,
        category=body.category,
        subject=body.subject,
        status="submitted",
        expires_on=body.expires_on,
        non_expiring=body.expires_on is None,
        file_name=body.file_name,
    )
    db.add(row)
    recompute(db, provider)
    db.commit()
    return provider_self(provider)


@router.get("/reviews")
def reviews(ctx: tuple[User, Provider] = Depends(require_provider), db: Session = Depends(get_db)):
    _, provider = ctx
    rows = db.query(Review).filter(Review.provider_id == provider.id, Review.status == "published").all()
    return {
        "results": [
            {"id": row.id, "rating": row.rating, "body": row.body, "alias": row.alias, "created_at": row.created_at.isoformat()}
            for row in rows
        ]
    }


@router.get("/membership")
def membership(ctx: tuple[User, Provider] = Depends(require_provider)):
    settings = get_settings()
    provider = ctx[1]
    return {
        "membership": provider.membership,
        "payment_status": provider.payment_status,
        "paid_through": provider.paid_through.isoformat() if provider.paid_through else None,
        "price_usd": settings.monthly_price_usd or None,
        "price_set": settings.price_set,
        "checkout": "web_portal_only",
        "note": "Membership is managed on this website. The installed app has no checkout, upgrade prompt, or purchase link.",
    }


@router.post("/membership/activate")
def activate(ctx: tuple[User, Provider] = Depends(require_provider), db: Session = Depends(get_db)):
    settings = get_settings()
    user, provider = ctx
    if settings.environment != "development" or not settings.allow_demo_payments:
        raise HTTPException(
            status_code=501,
            detail="PayPal checkout is not connected yet. Set the monthly price and PayPal before paid enrollment opens.",
        )
    provider.membership = "active"
    provider.payment_status = "succeeded"
    provider.paid_through = date.today() + timedelta(days=30)
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="demo_payment_succeeded",
            record_type="provider",
            record_id=str(provider.id),
            reason="Development payment recorded. Trust Score and verification were not changed.",
        )
    )
    db.commit()
    return membership(ctx)


@router.post("/membership/cancel")
def cancel(ctx: tuple[User, Provider] = Depends(require_provider), db: Session = Depends(get_db)):
    _, provider = ctx
    if provider.membership == "active":
        provider.membership = "cancelling"
    db.commit()
    return membership(ctx)
