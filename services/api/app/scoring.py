"""Trust Score baseline from the 20 November 2026 design package.

Verification 40%, feedback 20%, profile 15%, activity 15%, standing 10%.
A public number is withheld until registration is approved and every applicable
required check is current. Payment never enters the calculation.
"""

from __future__ import annotations

from datetime import date, datetime

WEIGHTS = {
    "verification": 0.40,
    "feedback": 0.20,
    "profile": 0.15,
    "activity": 0.15,
    "standing": 0.10,
}

BANDS = (
    (85, 100, "Excellent"),
    (70, 84, "Strong"),
    (50, 69, "Developing"),
    (0, 49, "Needs Review"),
)

REQUIRED_CATEGORIES = ("business_registration", "license", "insurance", "background")
PROFILE_SECTIONS = (
    "business",
    "description",
    "services",
    "suitability",
    "specialties",
    "area",
    "availability",
    "coverage",
    "rates",
    "experience",
    "picture",
)


def band_for(score: int) -> str:
    for low, high, label in BANDS:
        if low <= score <= high:
            return label
    return "Needs Review"


def feedback_factor(ratings: list[int]) -> float:
    if not ratings:
        return 50.0
    smoothed = (sum(ratings) + 3 * 3) / (len(ratings) + 3)
    return (smoothed - 1) / 4 * 100


def outcome_factor(yes_count: int, families: int) -> float:
    if families <= 0:
        return 50.0
    return (yes_count + 1.5) / (families + 3) * 100


def smoothed_ratio(successes: float, eligible: int) -> float:
    if eligible <= 0:
        return 50.0
    return (successes + 1.5) / (eligible + 3) * 100


def tenure_factor(active_days: int) -> float:
    return 50 + 50 * min(max(active_days, 0) / 365, 1)


def _expired(expires_on: date | None, non_expiring: bool, today: date) -> bool:
    if non_expiring or expires_on is None:
        return False
    return expires_on < today


def evidence_state(items: list[dict], today: date) -> tuple[bool, dict[str, float | None]]:
    """Return (publishable, factor values). None means the factor is omitted."""
    by_cat: dict[str, list[dict]] = {name: [] for name in REQUIRED_CATEGORIES}
    for item in items:
        if item["category"] in by_cat:
            by_cat[item["category"]].append(item)

    factors: dict[str, float | None] = {}
    publishable = True
    for category in REQUIRED_CATEGORIES:
        rows = by_cat[category]
        applicable = [row for row in rows if row["status"] != "not_applicable"]
        if not applicable:
            if any(row["status"] == "not_applicable" for row in rows):
                factors[category] = None
            else:
                factors[category] = 0.0
                publishable = False
            continue
        current = [
            row
            for row in applicable
            if row["status"] == "verified" and not _expired(row.get("expires_on"), row.get("non_expiring", False), today)
        ]
        if len(current) == len(applicable):
            factors[category] = 100.0
        else:
            factors[category] = 0.0
            publishable = False
    return publishable, factors


def completeness(flags: dict[str, bool]) -> float:
    filled = sum(1 for key in PROFILE_SECTIONS if flags.get(key))
    return filled / len(PROFILE_SECTIONS) * 100


def profile_factor(flags: dict[str, bool], accuracy: str) -> float:
    accuracy_points = {"verified": 100.0, "unchecked": 50.0, "inaccurate": 0.0}[accuracy]
    return (completeness(flags) + accuracy_points) / 2


def experience_factor(years: int | None, qualifications_reviewed: bool) -> float:
    if years is None or years < 0 or not qualifications_reviewed:
        return 50.0
    return 100.0


def weighted_total(category_scores: dict[str, float]) -> int:
    total = 0.0
    for name, weight in WEIGHTS.items():
        total += category_scores[name] * weight
    return int(round(total))


def _avg(values: list[float | None]) -> float:
    kept = [value for value in values if value is not None]
    if not kept:
        return 0.0
    return sum(kept) / len(kept)


def calculate(
    *,
    registration_approved: bool,
    evidence: list[dict],
    profile_flags: dict[str, bool],
    accuracy: str,
    years_experience: int | None,
    qualifications_reviewed: bool,
    ratings: list[int],
    yes_outcomes: int,
    outcome_families: int,
    timely_replies: int,
    eligible_replies: int,
    timely_renewals: int,
    renewal_count: int,
    unresolved_substantiated: bool,
    active_days: int,
    today: date | None = None,
) -> dict:
    today = today or date.today()
    publishable, evidence_factors = evidence_state(evidence, today)
    if not registration_approved:
        publishable = False

    verification_values = [
        100.0 if registration_approved and publishable else 0.0,
        evidence_factors.get("license"),
        evidence_factors.get("insurance"),
        evidence_factors.get("background"),
    ]
    categories = {
        "verification": _avg(verification_values),
        "feedback": feedback_factor(ratings),
        "profile": _avg(
            [
                profile_factor(profile_flags, accuracy),
                experience_factor(years_experience, qualifications_reviewed),
            ]
        ),
        "activity": _avg(
            [
                outcome_factor(yes_outcomes, outcome_families),
                smoothed_ratio(timely_replies, eligible_replies),
                smoothed_ratio(timely_renewals, renewal_count),
            ]
        ),
        "standing": _avg(
            [
                0.0 if unresolved_substantiated else 100.0,
                tenure_factor(active_days),
            ]
        ),
    }
    if not publishable:
        return {
            "state": "unavailable",
            "score": None,
            "label": None,
            "categories": {name: round(value, 1) for name, value in categories.items()},
            "weights": WEIGHTS,
            "disclaimer": "No public score until registration is approved and every applicable required check is current.",
        }
    score = weighted_total(categories)
    return {
        "state": "published",
        "score": score,
        "label": band_for(score),
        "categories": {name: round(value, 1) for name, value in categories.items()},
        "weights": WEIGHTS,
        "disclaimer": "This score is informational. It is not a guarantee of quality or safety.",
    }


def active_day_count(approved_at: datetime | None, today: date | None = None) -> int:
    if approved_at is None:
        return 0
    today = today or date.today()
    start = approved_at.date() if isinstance(approved_at, datetime) else approved_at
    return max((today - start).days, 0)
