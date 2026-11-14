"""Rules-based sorting guidance.

The model only says what material it sees. The advice comes from this fixed
table, so the app never shows invented disposal instructions.

The wording is general guidance written from common knowledge. It has not been
checked against a municipal source and must not be presented as official local
rules (see docs/decision-log.md).
"""

GUIDANCE = {
    "paper": {
        "bin": "Dry waste",
        "tips": [
            "Keep it clean and dry.",
            "Flatten cardboard boxes.",
            "Paper soaked in food or oil goes with wet waste.",
        ],
    },
    "plastic": {
        "bin": "Dry waste",
        "tips": [
            "Empty and rinse bottles and containers.",
            "Follow your local dry-waste rules; not every plastic is recycled.",
        ],
    },
    "metal": {
        "bin": "Dry waste",
        "tips": [
            "Rinse cans and tins.",
            "Keep metal containers separate from wet waste.",
        ],
    },
    "organic": {
        "bin": "Wet waste",
        "tips": [
            "Keep food and garden waste separate from dry waste.",
            "It can often be composted.",
        ],
    },
}

DISCLAIMER = (
    "Sorting and recycling rules vary by location. Check your local waste guidelines. "
    "Mixed-material or food-soiled items may need different handling."
)

NO_DETECTIONS_MESSAGE = (
    "No supported waste items were detected. Try a clearer photo with objects fully visible."
)
UNCERTAIN_MESSAGE = "Some items may be difficult to identify. Treat these results as estimates."
