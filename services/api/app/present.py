from app.catalog import SERVICE_LABELS
from app.models import Provider, Review


def public_provider(provider: Provider, reviews: list[Review] | None = None) -> dict:
    published = [row for row in (reviews or []) if row.status == "published"]
    return {
        "id": provider.id,
        "display_name": provider.display_name,
        "photo": provider.photo or "",
        "provider_type": provider.provider_type,
        "description": provider.description,
        "zip_code": provider.zip_code,
        "state": provider.state,
        "services": provider.services or [],
        "service_labels": [SERVICE_LABELS.get(item, item) for item in (provider.services or [])],
        "diagnoses": provider.diagnoses or [],
        "age_min": provider.age_min,
        "age_max": provider.age_max,
        "specialties": provider.specialties or [],
        "coverage_programs": provider.coverage_programs or [],
        "coverage_states": provider.coverage_states or [],
        "accepting": provider.accepting,
        "capacity": provider.capacity,
        "rates": provider.rates or [],
        "experience_years": provider.experience_years,
        "qualifications": provider.qualifications or "Not specified",
        "registration_status": provider.registration_status,
        "membership": provider.membership,
        "verified": provider.score_state == "published",
        "score": provider.score_value,
        "score_label": provider.score_label,
        "score_state": provider.score_state,
        "score_breakdown": provider.score_breakdown or {},
        "reviews": [
            {
                "id": row.id,
                "rating": row.rating,
                "body": row.body,
                "alias": row.alias,
                "created_at": row.created_at.isoformat(),
            }
            for row in published
        ],
    }


def provider_self(provider: Provider) -> dict:
    data = public_provider(provider)
    data.update(
        {
            "legal_name": provider.legal_name,
            "paid_through": provider.paid_through.isoformat() if provider.paid_through else None,
            "payment_status": provider.payment_status,
            "accuracy": provider.accuracy,
            "evidence": [
                {
                    "id": item.id,
                    "category": item.category,
                    "subject": item.subject,
                    "status": item.status,
                    "expires_on": item.expires_on.isoformat() if item.expires_on else None,
                    "file_name": item.file_name,
                    "note": item.note,
                }
                for item in provider.evidence
            ],
        }
    )
    return data
