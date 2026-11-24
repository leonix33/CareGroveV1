from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    failed_logins: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reset_token: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reset_expires: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    family: Mapped["FamilyProfile | None"] = relationship(back_populates="user", uselist=False)
    provider: Mapped["Provider | None"] = relationship(back_populates="user", uselist=False)


class FamilyProfile(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    phone: Mapped[str] = mapped_column(String(40), default="")
    zip_code: Mapped[str] = mapped_column(String(10), default="")
    state: Mapped[str] = mapped_column(String(2), default="")
    user: Mapped[User] = relationship(back_populates="family")
    recipients: Mapped[list["Recipient"]] = relationship(back_populates="family")


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    alias: Mapped[str] = mapped_column(String(80))
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    diagnosis: Mapped[str] = mapped_column(String(80), default="")
    needs: Mapped[str] = mapped_column(Text, default="")
    services: Mapped[list] = mapped_column(JSON, default=list)
    coverage: Mapped[list] = mapped_column(JSON, default=list)
    preferences: Mapped[list] = mapped_column(JSON, default=list)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    family: Mapped[FamilyProfile] = relationship(back_populates="recipients")


class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    legal_name: Mapped[str] = mapped_column(String(200), default="")
    display_name: Mapped[str] = mapped_column(String(200), default="")
    provider_type: Mapped[str] = mapped_column(String(80), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    zip_code: Mapped[str] = mapped_column(String(10), default="")
    state: Mapped[str] = mapped_column(String(2), default="")
    coverage_states: Mapped[list] = mapped_column(JSON, default=list)
    coverage_zips: Mapped[list] = mapped_column(JSON, default=list)
    services: Mapped[list] = mapped_column(JSON, default=list)
    diagnoses: Mapped[list] = mapped_column(JSON, default=list)
    age_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    age_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    specialties: Mapped[list] = mapped_column(JSON, default=list)
    coverage_programs: Mapped[list] = mapped_column(JSON, default=list)
    accepting: Mapped[str] = mapped_column(String(20), default="not_specified")
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rates: Mapped[list] = mapped_column(JSON, default=list)
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    qualifications: Mapped[str] = mapped_column(Text, default="")
    qualifications_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    accuracy: Mapped[str] = mapped_column(String(20), default="unchecked")
    has_picture: Mapped[bool] = mapped_column(Boolean, default=False)
    photo: Mapped[str] = mapped_column(String(120), default="")
    registration_status: Mapped[str] = mapped_column(String(20), default="pending")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    membership: Mapped[str] = mapped_column(String(20), default="free")
    paid_through: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_status: Mapped[str] = mapped_column(String(20), default="none")
    score_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_label: Mapped[str | None] = mapped_column(String(40), nullable=True)
    score_state: Mapped[str] = mapped_column(String(20), default="unavailable")
    score_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    unresolved_issue: Mapped[bool] = mapped_column(Boolean, default=False)
    user: Mapped[User] = relationship(back_populates="provider")
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="provider")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"))
    category: Mapped[str] = mapped_column(String(40))
    subject: Mapped[str] = mapped_column(String(40), default="company")
    status: Mapped[str] = mapped_column(String(20), default="missing")
    expires_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    non_expiring: Mapped[bool] = mapped_column(Boolean, default=False)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str] = mapped_column(Text, default="")
    provider: Mapped[Provider] = relationship(back_populates="evidence")


class SavedProvider(Base):
    __tablename__ = "saved_providers"
    __table_args__ = (UniqueConstraint("family_id", "provider_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"))


class ConnectionRequest(Base):
    __tablename__ = "connection_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("recipients.id"))
    service: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    disclosure: Mapped[str] = mapped_column(Text, default="")
    include_health: Mapped[bool] = mapped_column(Boolean, default=False)
    met_need: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (UniqueConstraint("family_id", "provider_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"))


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    sender_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = (UniqueConstraint("family_id", "provider_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"))
    blocked_by: Mapped[int] = mapped_column(ForeignKey("users.id"))


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("family_id", "provider_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"))
    rating: Mapped[int] = mapped_column(Integer)
    body: Mapped[str] = mapped_column(Text, default="")
    alias: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    decision_reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Concern(Base):
    __tablename__ = "concerns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"))
    subject: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(String(80))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")
    finding: Mapped[str] = mapped_column(String(40), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(80))
    record_type: Mapped[str] = mapped_column(String(40))
    record_id: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class SupportMessage(Base):
    __tablename__ = "support_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class DeletionRequest(Base):
    __tablename__ = "deletion_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="requested")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
