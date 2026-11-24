SERVICES = [
    {"id": "residential", "label": "Residential"},
    {"id": "respite", "label": "Respite"},
    {"id": "day_programs", "label": "Day programs"},
    {"id": "behavioral_support", "label": "Behavioral support"},
    {"id": "personal_care", "label": "Personal care"},
    {"id": "employment", "label": "Employment services"},
    {"id": "transportation", "label": "Transportation"},
    {"id": "therapy", "label": "Therapy"},
    {"id": "community", "label": "Community activities"},
    {"id": "autism_services", "label": "Autism services"},
    {"id": "supported_living", "label": "Supported living"},
]

DIAGNOSES = [
    {"id": "autism", "label": "Autism"},
    {"id": "idd", "label": "IDD"},
    {"id": "other", "label": "Other"},
    {"id": "not_specified", "label": "Not specified"},
]

PROVIDER_TYPES = [
    {"id": "agency", "label": "Agency"},
    {"id": "independent", "label": "Independent provider"},
    {"id": "residential", "label": "Residential program"},
]

COVERAGE = [
    {"id": "medicaid", "label": "Medicaid"},
    {"id": "waiver", "label": "Waiver"},
    {"id": "private_insurance", "label": "Private insurance"},
    {"id": "self_pay", "label": "Self-pay"},
]

STATES = ["TX", "IN"]

SERVICE_LABELS = {item["id"]: item["label"] for item in SERVICES}

# Approximate ZIP centers for launch examples. Distance is labeled as approximate.
ZIP_CENTERS = {
    "78701": (30.2672, -97.7431),
    "78704": (30.2430, -97.7650),
    "77002": (29.7560, -95.3570),
    "75201": (32.7876, -96.7990),
    "78205": (29.4241, -98.4936),
    "46204": (39.7684, -86.1581),
    "46802": (41.0793, -85.1394),
}
