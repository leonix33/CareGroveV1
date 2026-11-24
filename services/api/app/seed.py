from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.models import (
    ConnectionRequest,
    Conversation,
    Evidence,
    FamilyProfile,
    Message,
    Provider,
    Recipient,
    Review,
    User,
)
from app.security import hash_password
from app.trust import recompute

DEMO_PASSWORD = "CareGrove-demo-12"


def _user(db: Session, email: str, name: str, role: str) -> User:
    existing = db.query(User).filter(User.email == email).one_or_none()
    if existing:
        return existing
    user = User(
        email=email,
        name=name,
        role=role,
        password_hash=hash_password(DEMO_PASSWORD),
        email_verified=True,
        status="active",
    )
    db.add(user)
    db.flush()
    return user


def _evidence(provider: Provider, status: str = "verified", insurance_expires: date | None = None) -> None:
    for category in ("business_registration", "license", "insurance", "background"):
        expires = insurance_expires if category == "insurance" else None
        provider.evidence.append(
            Evidence(
                category=category,
                subject="company",
                status=status if category != "insurance" or insurance_expires is None else "verified",
                expires_on=expires,
                non_expiring=expires is None and status == "verified",
                file_name=f"{category}.pdf" if status != "missing" else None,
            )
        )


def seed(db: Session) -> None:
    if db.query(User).filter(User.email == "maya.chen@caregrove.demo").one_or_none():
        return

    admin = _user(db, "admin@caregrove.demo", "CareGrove Staff", "admin")
    maya = _user(db, "maya.chen@caregrove.demo", "Maya Chen", "family")
    jordan = _user(db, "jordan.lee@caregrove.demo", "Jordan Lee", "family")

    maya_family = FamilyProfile(user_id=maya.id, phone="512-555-0148", zip_code="78704", state="TX")
    jordan_family = FamilyProfile(user_id=jordan.id, phone="317-555-0190", zip_code="46204", state="IN")
    db.add_all([maya_family, jordan_family])
    db.flush()
    alex = Recipient(
        family_id=maya_family.id,
        alias="Alex",
        age=14,
        diagnosis="autism",
        needs="After-school respite and help with daily routines.",
        services=["respite", "personal_care"],
        coverage=["medicaid"],
        preferences=["agency"],
    )
    sam = Recipient(
        family_id=jordan_family.id,
        alias="Sam",
        age=22,
        diagnosis="idd",
        needs="Day program and community time.",
        services=["day_programs"],
        coverage=["waiver"],
        preferences=[],
    )
    db.add_all([alex, sam])
    db.flush()

    def provider(email, name, **fields) -> Provider:
        user = _user(db, email, name, "provider")
        row = Provider(user_id=user.id, display_name=name, legal_name=f"{name} LLC", **fields)
        db.add(row)
        db.flush()
        return row

    approved = datetime(2025, 6, 1)
    oak = provider(
        "oak@caregrove.demo",
        "Bright Path Services",
        provider_type="agency",
        description="Residential and respite for autistic youth. Premium listing.",
        zip_code="78701",
        state="TX",
        coverage_states=["TX", "IN"],
        services=["respite", "residential", "personal_care", "autism_services"],
        photo="bright-path.jpg",
        diagnoses=["autism", "idd"],
        age_min=6,
        age_max=21,
        specialties=["autism"],
        coverage_programs=["medicaid", "waiver"],
        accepting="accepting",
        capacity=8,
        rates=[{"service": "respite", "amount": 32, "unit": "hour"}],
        experience_years=11,
        qualifications="State-reviewed agency credentials on file.",
        qualifications_reviewed=True,
        accuracy="verified",
        has_picture=True,
        registration_status="approved",
        approved_at=approved,
        membership="active",
        paid_through=date(2027, 1, 15),
        payment_status="succeeded",
    )
    harbor = provider(
        "harbor@caregrove.demo",
        "Harbor Respite Co",
        provider_type="agency",
        description="Short-term respite across the Houston area.",
        zip_code="77002",
        state="TX",
        coverage_states=["TX"],
        services=["respite"],
        diagnoses=["autism", "idd"],
        age_min=5,
        age_max=18,
        specialties=["respite"],
        coverage_programs=["medicaid", "self_pay"],
        accepting="accepting",
        capacity=5,
        rates=[{"service": "respite", "amount": 28, "unit": "hour"}],
        experience_years=6,
        qualifications="Respite certification submitted.",
        qualifications_reviewed=True,
        accuracy="verified",
        has_picture=False,
        registration_status="approved",
        approved_at=approved,
        membership="active",
        paid_through=date(2027, 2, 1),
        payment_status="succeeded",
    )
    lantern = provider(
        "lantern@caregrove.demo",
        "Lantern Day Program",
        provider_type="residential",
        description="Weekday day programs in Dallas. Free directory listing.",
        zip_code="75201",
        state="TX",
        coverage_states=["TX"],
        services=["day_programs", "community"],
        diagnoses=["idd", "autism"],
        age_min=16,
        age_max=40,
        specialties=["day programs"],
        coverage_programs=["waiver", "medicaid"],
        accepting="accepting",
        capacity=20,
        rates=[{"service": "day_programs", "amount": 140, "unit": "day"}],
        experience_years=9,
        qualifications="Day program accreditation reviewed.",
        qualifications_reviewed=True,
        accuracy="verified",
        has_picture=True,
        registration_status="approved",
        approved_at=approved,
        membership="free",
        payment_status="none",
    )
    northwind = provider(
        "northwind@caregrove.demo",
        "Evergreen Support",
        provider_type="independent",
        description="Residential and respite. Standard free directory listing.",
        zip_code="46204",
        state="IN",
        coverage_states=["IN", "TX"],
        services=["respite", "residential", "personal_care"],
        photo="evergreen.jpg",
        diagnoses=["autism"],
        age_min=8,
        age_max=25,
        specialties=[],
        coverage_programs=["medicaid"],
        accepting="accepting",
        capacity=3,
        rates=[],
        experience_years=2,
        qualifications="Credentials reviewed. Free directory listing.",
        qualifications_reviewed=True,
        accuracy="verified",
        has_picture=True,
        registration_status="approved",
        approved_at=datetime(2026, 10, 1),
        membership="free",
        payment_status="none",
    )
    mesa = provider(
        "mesa@caregrove.demo",
        "Mesa Personal Care",
        provider_type="agency",
        description="Personal care in San Antonio. Insurance on file is expired.",
        zip_code="78205",
        state="TX",
        coverage_states=["TX"],
        services=["personal_care"],
        diagnoses=["idd", "autism"],
        age_min=10,
        age_max=65,
        specialties=["personal care"],
        coverage_programs=["medicaid"],
        accepting="accepting",
        capacity=12,
        rates=[{"service": "personal_care", "amount": 24, "unit": "hour"}],
        experience_years=15,
        qualifications="Agency qualifications on file.",
        qualifications_reviewed=True,
        accuracy="verified",
        has_picture=False,
        registration_status="approved",
        approved_at=approved,
        membership="free",
        payment_status="none",
    )
    prairie = provider(
        "prairie@caregrove.demo",
        "CareBridge Therapy",
        provider_type="agency",
        description="Therapy and autism services. Premium listing.",
        zip_code="78701",
        state="TX",
        coverage_states=["TX", "IN"],
        services=["therapy", "autism_services", "respite"],
        photo="carebridge.jpg",
        diagnoses=["autism"],
        age_min=4,
        age_max=18,
        specialties=["therapy"],
        coverage_programs=["medicaid", "waiver", "private_insurance"],
        accepting="accepting",
        capacity=10,
        rates=[{"service": "therapy", "amount": 150, "unit": "session"}],
        experience_years=7,
        qualifications="Therapy credentials reviewed.",
        qualifications_reviewed=True,
        accuracy="verified",
        has_picture=True,
        registration_status="approved",
        approved_at=approved,
        membership="active",
        paid_through=date(2027, 3, 1),
        payment_status="succeeded",
    )

    for row in (oak, harbor, lantern, prairie, northwind):
        _evidence(row, "verified")
    _evidence(mesa, "verified", insurance_expires=date(2024, 1, 1))

    request = ConnectionRequest(
        family_id=maya_family.id,
        provider_id=oak.id,
        recipient_id=alex.id,
        service="respite",
        status="pending",
        disclosure="Alex, age 14. Service: respite. Diagnosis shared by choice.",
        include_health=True,
    )
    db.add(request)
    conversation = Conversation(family_id=maya_family.id, provider_id=oak.id)
    db.add(conversation)
    db.flush()
    db.add(
        Message(
            conversation_id=conversation.id,
            sender_user_id=maya.id,
            body="Hello. We are looking for weekday afternoon respite for Alex.",
            created_at=datetime.utcnow() - timedelta(hours=5),
        )
    )
    completed = ConnectionRequest(
        family_id=jordan_family.id,
        provider_id=harbor.id,
        recipient_id=sam.id,
        service="respite",
        status="completed",
        disclosure="Sam, age 22. Service: respite.",
        include_health=False,
        met_need=True,
        completed_at=datetime.utcnow() - timedelta(days=12),
    )
    db.add(completed)
    db.add(
        Review(
            family_id=jordan_family.id,
            provider_id=oak.id,
            rating=5,
            body="Clear communication and steady respite coverage.",
            alias="Jordan L.",
            status="published",
        )
    )
    db.add(
        Review(
            family_id=maya_family.id,
            provider_id=harbor.id,
            rating=4,
            body="Waiting for staff to check this review before it is public.",
            alias="Maya C.",
            status="pending",
        )
    )
    db.flush()
    for row in (oak, harbor, lantern, northwind, mesa, prairie):
        recompute(db, row)
    db.commit()
    _ = admin
