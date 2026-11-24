from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import DeletionRequest, SupportMessage

router = APIRouter(prefix="/public", tags=["public"])


class SupportIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=255)
    body: str = Field(min_length=4, max_length=4000)


class DeletionIn(BaseModel):
    email: str
    role: str


PRIVACY = (
    "This wording is illustrative until the privacy policy is approved. "
    "Profiles: provider business listings are public on the directory. "
    "Recipient needs are visible only to the provider a family contacts, and only when the family chooses to include them. "
    "Evidence and credentials stay private for staff review. "
    "Messages stay between the family and the provider. "
    "CareGrove introduces families and providers. Care itself happens offline."
)


@router.get("/privacy")
def privacy():
    return {"title": "Privacy Safeguards", "body": PRIVACY, "illustrative": True}


@router.post("/support")
def support(body: SupportIn, db: Session = Depends(get_db)):
    db.add(SupportMessage(name=body.name.strip(), email=body.email.strip(), body=body.body.strip()))
    db.commit()
    return {"message": "Message received. The support team can reply by email."}


@router.post("/deletion")
def deletion(body: DeletionIn, db: Session = Depends(get_db)):
    if body.role in {"family", "provider"}:
        db.add(DeletionRequest(email=body.email.strip().lower(), role=body.role))
        db.commit()
    return {
        "message": "If an account exists, a deletion request was recorded. A verification email is required before anything is removed."
    }
