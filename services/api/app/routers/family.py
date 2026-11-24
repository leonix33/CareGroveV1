from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.catalog import COVERAGE, DIAGNOSES, SERVICES, STATES
from app.db import get_db
from app.deps import require_family
from app.models import FamilyProfile, Recipient, User

router = APIRouter(tags=["family"])


class ProfileIn(BaseModel):
    phone: str = ""
    zip_code: str
    state: str


class RecipientIn(BaseModel):
    alias: str = Field(min_length=1, max_length=80)
    age: int | None = Field(default=None, ge=0, le=120)
    diagnosis: str = ""
    needs: str = Field(default="", max_length=1000)
    services: list[str] = []
    coverage: list[str] = []
    preferences: list[str] = []


@router.get("/catalog")
def catalog():
    return {"services": SERVICES, "diagnoses": DIAGNOSES, "coverage": COVERAGE, "states": STATES}


@router.get("/family/profile")
def get_profile(ctx: tuple[User, FamilyProfile] = Depends(require_family)):
    _, family = ctx
    return {
        "phone": family.phone,
        "zip_code": family.zip_code,
        "state": family.state,
        "recipients": [_recipient(row) for row in family.recipients],
    }


@router.put("/family/profile")
def update_profile(body: ProfileIn, ctx: tuple[User, FamilyProfile] = Depends(require_family), db: Session = Depends(get_db)):
    _, family = ctx
    if body.state not in STATES:
        raise HTTPException(status_code=400, detail="CareGrove is launching in Texas and Indiana")
    if len(body.zip_code.strip()) < 5:
        raise HTTPException(status_code=400, detail="Enter a ZIP code")
    family.phone = body.phone.strip()
    family.zip_code = body.zip_code.strip()
    family.state = body.state
    db.commit()
    return {"ok": True}


@router.post("/family/recipients")
def add_recipient(body: RecipientIn, ctx: tuple[User, FamilyProfile] = Depends(require_family), db: Session = Depends(get_db)):
    _, family = ctx
    row = Recipient(family_id=family.id, **body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return _recipient(row)


@router.patch("/family/recipients/{recipient_id}")
def edit_recipient(
    recipient_id: int,
    body: RecipientIn,
    ctx: tuple[User, FamilyProfile] = Depends(require_family),
    db: Session = Depends(get_db),
):
    _, family = ctx
    row = _own_recipient(db, family, recipient_id)
    for key, value in body.model_dump().items():
        setattr(row, key, value)
    db.commit()
    return _recipient(row)


@router.post("/family/recipients/{recipient_id}/archive")
def archive_recipient(recipient_id: int, ctx: tuple[User, FamilyProfile] = Depends(require_family), db: Session = Depends(get_db)):
    _, family = ctx
    row = _own_recipient(db, family, recipient_id)
    row.archived = True
    db.commit()
    return _recipient(row)


def _own_recipient(db: Session, family: FamilyProfile, recipient_id: int) -> Recipient:
    row = db.get(Recipient, recipient_id)
    if row is None or row.family_id != family.id:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return row


def _recipient(row: Recipient) -> dict:
    return {
        "id": row.id,
        "alias": row.alias,
        "age": row.age,
        "diagnosis": row.diagnosis,
        "needs": row.needs,
        "services": row.services or [],
        "coverage": row.coverage or [],
        "preferences": row.preferences or [],
        "archived": row.archived,
    }
