from datetime import date, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.matching import all_providers, suggested_matches
from app.models import Base, FamilyProfile, Provider, Recipient, User
from app.security import hash_password


def _session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _family(db):
    user = User(email="family@example.com", password_hash=hash_password("CareGrove-demo-12"), name="Family", role="family", email_verified=True)
    db.add(user)
    db.flush()
    family = FamilyProfile(user_id=user.id, zip_code="78704", state="TX")
    db.add(family)
    db.flush()
    recipient = Recipient(
        family_id=family.id,
        alias="Alex",
        age=14,
        diagnosis="autism",
        services=["respite"],
        coverage=["medicaid"],
    )
    db.add(recipient)
    db.flush()
    return family, recipient


def _provider(db, email, name, membership, services):
    user = User(email=email, password_hash="x", name=name, role="provider", email_verified=True, status="active")
    db.add(user)
    db.flush()
    provider = Provider(
        user_id=user.id,
        display_name=name,
        legal_name=name,
        zip_code="78701",
        state="TX",
        coverage_states=["TX"],
        services=services,
        diagnoses=["autism"],
        age_min=6,
        age_max=21,
        coverage_programs=["medicaid"],
        accepting="accepting",
        capacity=4,
        registration_status="approved",
        approved_at=datetime(2025, 1, 1),
        membership=membership,
        paid_through=date(2027, 1, 1) if membership == "active" else None,
        payment_status="succeeded" if membership == "active" else "none",
        score_value=80 if membership == "active" else 60,
        score_label="Strong" if membership == "active" else "Developing",
        score_state="published",
    )
    db.add(provider)
    db.flush()
    return provider


def test_premium_pool_is_not_topped_up_with_free_providers():
    db = _session()
    family, recipient = _family(db)
    premium = _provider(db, "p@example.com", "Premium Care", "active", ["respite"])
    free = _provider(db, "f@example.com", "Free Care", "free", ["respite"])
    db.commit()

    suggested = suggested_matches(
        db, family_id=family.id, family_zip="78704", family_state="TX", recipient=recipient, service="respite"
    )
    directory = all_providers(db, family_id=family.id, family_zip="78704")

    assert suggested["pool"] == "premium"
    assert [row["id"] for row in suggested["results"]] == [premium.id]
    assert {row["id"] for row in directory} == {premium.id, free.id}


def test_free_fallback_only_when_no_suitable_premium_provider_qualifies():
    db = _session()
    family, recipient = _family(db)
    free_a = _provider(db, "a@example.com", "Free A", "free", ["respite"])
    free_b = _provider(db, "b@example.com", "Free B", "free", ["respite"])
    _provider(db, "c@example.com", "Premium Other Service", "active", ["therapy"])
    db.commit()

    suggested = suggested_matches(
        db, family_id=family.id, family_zip="78704", family_state="TX", recipient=recipient, service="respite"
    )
    assert suggested["pool"] == "free_fallback"
    assert {row["id"] for row in suggested["results"]} == {free_a.id, free_b.id}
    assert "No suitable premium" in suggested["explanation"]


def test_activating_premium_removes_the_other_free_provider_from_suggestions():
    db = _session()
    family, recipient = _family(db)
    first = _provider(db, "a@example.com", "Free A", "free", ["respite"])
    second = _provider(db, "b@example.com", "Free B", "free", ["respite"])
    db.commit()
    before = suggested_matches(
        db, family_id=family.id, family_zip="78704", family_state="TX", recipient=recipient, service="respite"
    )
    assert before["pool"] == "free_fallback"
    assert {row["id"] for row in before["results"]} == {first.id, second.id}

    second.membership = "active"
    second.payment_status = "succeeded"
    second.paid_through = date(2027, 1, 1)
    db.commit()

    after = suggested_matches(
        db, family_id=family.id, family_zip="78704", family_state="TX", recipient=recipient, service="respite"
    )
    directory = all_providers(db, family_id=family.id, family_zip="78704")
    assert [row["id"] for row in after["results"]] == [second.id]
    assert {row["id"] for row in directory} == {first.id, second.id}


def test_unsuitable_provider_is_excluded_even_when_premium():
    db = _session()
    family, recipient = _family(db)
    wrong_age = _provider(db, "old@example.com", "Adults Only", "active", ["respite"])
    wrong_age.age_min = 30
    wrong_age.age_max = 50
    db.commit()
    suggested = suggested_matches(
        db, family_id=family.id, family_zip="78704", family_state="TX", recipient=recipient, service="respite"
    )
    assert suggested["pool"] == "none"
    assert suggested["results"] == []
