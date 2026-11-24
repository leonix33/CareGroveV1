from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.models import ConnectionRequest, Evidence, Message, Provider, Review
from app.scoring import active_day_count, calculate


def recompute(db: Session, provider: Provider, today: date | None = None) -> dict:
    today = today or date.today()
    evidence = [
        {
            "category": item.category,
            "status": item.status,
            "expires_on": item.expires_on,
            "non_expiring": item.non_expiring,
        }
        for item in provider.evidence
    ]
    ratings = [
        row.rating
        for row in db.query(Review).filter(Review.provider_id == provider.id, Review.status == "published")
    ]
    outcomes = (
        db.query(ConnectionRequest)
        .filter(
            ConnectionRequest.provider_id == provider.id,
            ConnectionRequest.status == "completed",
            ConnectionRequest.met_need.isnot(None),
        )
        .all()
    )
    latest: dict[int, ConnectionRequest] = {}
    for outcome in outcomes:
        current = latest.get(outcome.family_id)
        if current is None or (outcome.completed_at or datetime.min) >= (current.completed_at or datetime.min):
            latest[outcome.family_id] = outcome
    yes_count = sum(1 for row in latest.values() if row.met_need)
    flags = {
        "business": bool(provider.display_name and provider.legal_name),
        "description": bool(provider.description),
        "services": bool(provider.services),
        "suitability": bool(provider.diagnoses and provider.age_min is not None),
        "specialties": bool(provider.specialties),
        "area": bool(provider.zip_code and provider.state),
        "availability": provider.accepting != "not_specified" and provider.capacity is not None,
        "coverage": bool(provider.coverage_programs),
        "rates": bool(provider.rates),
        "experience": provider.experience_years is not None and bool(provider.qualifications),
        "picture": provider.has_picture,
    }
    result = calculate(
        registration_approved=provider.registration_status == "approved",
        evidence=evidence,
        profile_flags=flags,
        accuracy=provider.accuracy,
        years_experience=provider.experience_years,
        qualifications_reviewed=provider.qualifications_reviewed,
        ratings=ratings,
        yes_outcomes=yes_count,
        outcome_families=len(latest),
        timely_replies=_timely_replies(db, provider.id),
        eligible_replies=_eligible_replies(db, provider.id),
        timely_renewals=0,
        renewal_count=0,
        unresolved_substantiated=provider.unresolved_issue,
        active_days=active_day_count(provider.approved_at, today),
        today=today,
    )
    provider.score_value = result["score"]
    provider.score_label = result["label"]
    provider.score_state = result["state"]
    provider.score_breakdown = result
    db.add(provider)
    return result


def _provider_user_id(db: Session, provider_id: int) -> int | None:
    provider = db.get(Provider, provider_id)
    return provider.user_id if provider else None


def _eligible_replies(db: Session, provider_id: int) -> int:
    return len(_turns(db, provider_id))


def _timely_replies(db: Session, provider_id: int) -> int:
    return sum(1 for hours in _turns(db, provider_id) if hours is not None and hours <= 48)


def _turns(db: Session, provider_id: int) -> list[float | None]:
    """One turn is a family message group until the next provider reply."""
    provider = db.get(Provider, provider_id)
    if provider is None:
        return []
    from app.models import Conversation

    conversations = db.query(Conversation).filter(Conversation.provider_id == provider_id).all()
    hours: list[float | None] = []
    now = datetime.utcnow()
    for conversation in conversations:
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        waiting_since: datetime | None = None
        for message in messages:
            from_provider = message.sender_user_id == provider.user_id
            if not from_provider:
                waiting_since = waiting_since or message.created_at
                continue
            if waiting_since is not None:
                delta = message.created_at - waiting_since
                hours.append(delta.total_seconds() / 3600)
                waiting_since = None
        if waiting_since is not None:
            elapsed = now - waiting_since
            if elapsed > timedelta(hours=48):
                hours.append(None)
    return hours
