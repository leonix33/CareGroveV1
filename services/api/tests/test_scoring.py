from datetime import date

from app.scoring import band_for, calculate, feedback_factor, outcome_factor


def _evidence(status="verified", expires=None):
    return [
        {"category": name, "status": status, "expires_on": expires, "non_expiring": expires is None}
        for name in ("business_registration", "license", "insurance", "background")
    ]


def _flags():
    return {key: True for key in (
        "business", "description", "services", "suitability", "specialties",
        "area", "availability", "coverage", "rates", "experience", "picture",
    )}


def test_feedback_smoothing_limits_a_single_review():
    assert feedback_factor([]) == 50
    one_star = feedback_factor([1])
    five_star = feedback_factor([5])
    assert one_star < 50 < five_star
    assert abs(five_star - one_star) < 55


def test_missing_required_evidence_withholds_the_public_score():
    result = calculate(
        registration_approved=True,
        evidence=[],
        profile_flags=_flags(),
        accuracy="verified",
        years_experience=8,
        qualifications_reviewed=True,
        ratings=[5, 5],
        yes_outcomes=2,
        outcome_families=2,
        timely_replies=2,
        eligible_replies=2,
        timely_renewals=0,
        renewal_count=0,
        unresolved_substantiated=False,
        active_days=400,
    )
    assert result["state"] == "unavailable"
    assert result["score"] is None


def test_published_score_uses_bands_and_ignores_payment():
    result = calculate(
        registration_approved=True,
        evidence=_evidence(),
        profile_flags=_flags(),
        accuracy="verified",
        years_experience=8,
        qualifications_reviewed=True,
        ratings=[5, 4, 5],
        yes_outcomes=3,
        outcome_families=3,
        timely_replies=4,
        eligible_replies=4,
        timely_renewals=1,
        renewal_count=1,
        unresolved_substantiated=False,
        active_days=400,
        today=date(2026, 11, 23),
    )
    assert result["state"] == "published"
    assert result["label"] == band_for(result["score"])
    assert 0 <= result["score"] <= 100
    assert result["label"] in {"Excellent", "Strong"}


def test_expired_insurance_removes_publication():
    result = calculate(
        registration_approved=True,
        evidence=_evidence(expires=date(2020, 1, 1)),
        profile_flags=_flags(),
        accuracy="verified",
        years_experience=4,
        qualifications_reviewed=True,
        ratings=[],
        yes_outcomes=0,
        outcome_families=0,
        timely_replies=0,
        eligible_replies=0,
        timely_renewals=0,
        renewal_count=0,
        unresolved_substantiated=False,
        active_days=10,
        today=date(2026, 11, 23),
    )
    assert result["score"] is None


def test_outcome_factor_does_not_treat_silence_as_failure():
    assert outcome_factor(0, 0) == 50
