"""Rules-based sorting guidance.

The model only says what material it sees. The advice comes from this fixed
table, so the app never shows invented disposal instructions.
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
            "It can be composted.",
        ],
    },
}

DISCLAIMER = (
    "General guidance only. Local municipal rules can differ, and mixed-material "
    "or food-soiled items may need different handling."
)
