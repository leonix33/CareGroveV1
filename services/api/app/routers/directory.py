from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_family
from app.matching import all_providers, suggested_matches
from app.models import FamilyProfile, Provider, Recipient, Review, SavedProvider, User
from app.present import public_provider

router = APIRouter(tags=["directory"])


@router.get("/family/suggestions")
def suggestions(
    recipient_id: int,
    service: str,
    ctx: tuple[User, FamilyProfile] = Depends(require_family),
    db: Session = Depends(get_db),
):
    _, family = ctx
    recipient = db.get(Recipient, recipient_id)
    if recipient is None or recipient.family_id != family.id or recipient.archived:
        raise HTTPException(status_code=404, detail="Choose an active recipient")
    if not family.zip_code or not family.state:
        raise HTTPException(status_code=400, detail="Add a Texas or Indiana ZIP before matching")
    return suggested_matches(
        db,
        family_id=family.id,
        family_zip=family.zip_code,
        family_state=family.state,
        recipient=recipient,
        service=service,
    )


@router.get("/family/providers")
def directory(ctx: tuple[User, FamilyProfile] = Depends(require_family), db: Session = Depends(get_db)):
    _, family = ctx
    return {"results": all_providers(db, family_id=family.id, family_zip=family.zip_code)}


@router.get("/providers/{provider_id}")
def provider_detail(provider_id: int, db: Session = Depends(get_db)):
    provider = db.get(Provider, provider_id)
    if provider is None or provider.registration_status != "approved" or provider.user.status != "active":
        raise HTTPException(status_code=404, detail="Provider is not available")
    reviews = db.query(Review).filter(Review.provider_id == provider.id).all()
    return public_provider(provider, reviews)


@router.post("/family/saved/{provider_id}")
def save_provider(provider_id: int, ctx: tuple[User, FamilyProfile] = Depends(require_family), db: Session = Depends(get_db)):
    _, family = ctx
    if db.get(Provider, provider_id) is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    existing = (
        db.query(SavedProvider)
        .filter(SavedProvider.family_id == family.id, SavedProvider.provider_id == provider_id)
        .one_or_none()
    )
    if existing is None:
        db.add(SavedProvider(family_id=family.id, provider_id=provider_id))
        db.commit()
    return {"saved": True}


@router.delete("/family/saved/{provider_id}")
def unsave_provider(provider_id: int, ctx: tuple[User, FamilyProfile] = Depends(require_family), db: Session = Depends(get_db)):
    _, family = ctx
    db.query(SavedProvider).filter(SavedProvider.family_id == family.id, SavedProvider.provider_id == provider_id).delete()
    db.commit()
    return {"saved": False}


@router.get("/family/saved")
def saved(ctx: tuple[User, FamilyProfile] = Depends(require_family), db: Session = Depends(get_db)):
    _, family = ctx
    rows = db.query(SavedProvider).filter(SavedProvider.family_id == family.id).all()
    results = []
    for row in rows:
        provider = db.get(Provider, row.provider_id)
        if provider:
            results.append(
                {
                    "id": provider.id,
                    "display_name": provider.display_name,
                    "state": provider.state,
                    "score": provider.score_value,
                    "score_label": provider.score_label,
                    "score_state": provider.score_state,
                    "membership": provider.membership,
                    "available": provider.registration_status == "approved" and provider.user.status == "active",
                }
            )
    return {"results": results}
