"""Suggested matches: suitability, then premium pool, then free fallback.

Membership changes who is eligible for the suggestion pool. It does not change
verification, suitability, or Trust Score, and it never fills a nonempty premium
pool with free providers.
"""

from __future__ import annotations

import math

from sqlalchemy.orm import Session

from app.catalog import SERVICE_LABELS, ZIP_CENTERS
from app.models import Block, Provider, Recipient, SavedProvider, User


def _miles(origin: str, destination: str) -> float | None:
    a = ZIP_CENTERS.get(origin)
    b = ZIP_CENTERS.get(destination)
    if not a or not b:
        return None
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return round(3958.8 * 2 * math.asin(math.sqrt(h)), 1)


def _discoverable(provider: Provider) -> bool:
    user = provider.user
    return provider.registration_status == "approved" and user is not None and user.status == "active"


def suitability_reasons(provider: Provider, recipient: Recipient, service: str, family_zip: str, family_state: str) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if service not in (provider.services or []):
        return False, []
    reasons.append(SERVICE_LABELS.get(service, service))

    if recipient.age is not None:
        low = provider.age_min if provider.age_min is not None else 0
        high = provider.age_max if provider.age_max is not None else 120
        if not (low <= recipient.age <= high):
            return False, []
        reasons.append(f"Ages {low}–{high}")

    diagnosis = recipient.diagnosis
    supported = provider.diagnoses or []
    if diagnosis and diagnosis not in ("", "not_specified"):
        if supported and diagnosis not in supported and "any" not in supported:
            return False, []
        if diagnosis in supported:
            reasons.append("Diagnosis listed")

    needed = set(recipient.coverage or [])
    accepted = set(provider.coverage_programs or [])
    if needed and not (needed & accepted):
        return False, []
    if needed & accepted:
        reasons.append("Coverage listed")

    if provider.accepting != "accepting":
        return False, []

    states = provider.coverage_states or []
    zips = provider.coverage_zips or []
    if family_state and states and family_state not in states and "ALL" not in states:
        return False, []
    if zips and family_zip and family_zip not in zips and family_state not in states:
        return False, []

    if provider.state:
        reasons.append(provider.state)
    return True, reasons


def _premium(provider: Provider) -> bool:
    return provider.membership == "active"


def _card(provider: Provider, family_zip: str, reasons: list[str], saved_ids: set[int]) -> dict:
    miles = _miles(family_zip, provider.zip_code)
    return {
        "id": provider.id,
        "display_name": provider.display_name,
        "provider_type": provider.provider_type,
        "services": provider.services or [],
        "city_zip": provider.zip_code,
        "state": provider.state,
        "distance_miles": miles,
        "distance_label": None if miles is None else f"About {miles} mi from base ZIP",
        "score": provider.score_value,
        "score_label": provider.score_label,
        "score_state": provider.score_state,
        "verified": provider.score_state == "published" and _verified_badge(provider),
        "membership": provider.membership,
        "accepting": provider.accepting,
        "photo": provider.photo or "",
        "match_reasons": reasons,
        "saved": provider.id in saved_ids,
    }


def _verified_badge(provider: Provider) -> bool:
    return provider.registration_status == "approved" and provider.score_state == "published"


def _sort_key(card: dict, provider_id: int) -> tuple:
    unavailable = card["score"] is None
    distance = card["distance_miles"] if card["distance_miles"] is not None else 10_000
    return (unavailable, -(card["score"] or 0), distance, provider_id)


def _saved_ids(db: Session, family_id: int) -> set[int]:
    rows = db.query(SavedProvider).filter(SavedProvider.family_id == family_id).all()
    return {row.provider_id for row in rows}


def _blocked(db: Session, family_id: int) -> set[int]:
    rows = db.query(Block).filter(Block.family_id == family_id).all()
    return {row.provider_id for row in rows}


def suggested_matches(db: Session, *, family_id: int, family_zip: str, family_state: str, recipient: Recipient, service: str) -> dict:
    saved = _saved_ids(db, family_id)
    blocked = _blocked(db, family_id)
    providers = db.query(Provider).join(User).all()
    premium: list[tuple[Provider, list[str]]] = []
    free: list[tuple[Provider, list[str]]] = []
    for provider in providers:
        if not _discoverable(provider) or provider.id in blocked:
            continue
        ok, reasons = suitability_reasons(provider, recipient, service, family_zip, family_state)
        if not ok:
            continue
        if _premium(provider):
            premium.append((provider, reasons))
        else:
            free.append((provider, reasons))

    if premium:
        pool = "premium"
        chosen = premium
        explanation = "Showing suitable providers with an active membership. Free providers stay in All providers."
    elif free:
        pool = "free_fallback"
        chosen = free
        explanation = "No suitable premium providers qualify. Showing suitable free providers instead."
    else:
        pool = "none"
        chosen = []
        explanation = "No suitable providers match the required criteria. You can still browse All providers."

    cards = [_card(provider, family_zip, reasons, saved) for provider, reasons in chosen]
    cards.sort(key=lambda card: _sort_key(card, card["id"]))
    return {"pool": pool, "explanation": explanation, "service": service, "results": cards}


def all_providers(db: Session, *, family_id: int, family_zip: str) -> list[dict]:
    saved = _saved_ids(db, family_id)
    providers = db.query(Provider).join(User).all()
    cards = []
    for provider in providers:
        if not _discoverable(provider):
            continue
        cards.append(_card(provider, family_zip, [], saved))
    cards.sort(key=lambda card: _sort_key(card, card["id"]))
    return cards
