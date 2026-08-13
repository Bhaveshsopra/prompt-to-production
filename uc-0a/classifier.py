"""
UC-0A — Complaint Classifier
Built using agents.md + skills.md enforcement rules.
"""

import argparse
import csv


ALLOWED_CATEGORIES = {
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
}

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]


def find_match(text, keywords):
    """Return the first matching keyword."""
    for keyword in keywords:
        if keyword in text:
            return keyword
    return None


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")

    description = (
        row.get("description")
        or row.get("complaint")
        or row.get("text")
        or row.get("complaint_description")
        or ""
    )

    description = str(description).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No complaint description was provided.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    severity_match = find_match(text, SEVERITY_KEYWORDS)

    if severity_match:
        priority = "Urgent"
    else:
        priority = "Standard"

    category = "Other"
    category_match = None

    rules = [
        (
            "Pothole",
            ["pothole"],
        ),
        (
            "Flooding",
            ["flood", "flooding", "waterlogged", "water logging"],
        ),
        (
            "Streetlight",
            ["streetlight", "street light", "lamp post"],
        ),
        (
            "Waste",
            ["garbage", "waste", "trash", "rubbish", "dumped"],
        ),
        (
            "Noise",
            ["noise", "loud music", "loudspeaker", "music past midnight"],
        ),
        (
            "Road Damage",
            [
                "road damage",
                "damaged road",
                "cracked road",
                "road surface",
                "cracked",
                "sinking",
                "broken",
                "footpath tiles",
                "upturned",
            ],
        ),
        (
            "Heritage Damage",
            ["heritage", "monument", "historical building"],
        ),
        (
            "Heat Hazard",
            ["heatwave", "heat wave", "extreme heat", "heat hazard"],
        ),
        (
            "Drain Blockage",
            ["drain", "drainage", "blocked drain", "manhole"],
        ),
    ]

    for possible_category, keywords in rules:
        match = find_match(text, keywords)

        if match:
            category = possible_category
            category_match = match
            break

    flag = ""

    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = (
            f'No allowed category keyword was clearly identified in '
            f'the description: "{description}".'
        )
    else:
        reason = (
            f'The word/phrase "{category_match}" in the description '
            f'supports the category {category}.'
        )

        if severity_match:
            reason += (
                f' The severity keyword "{severity_match}" makes the '
                f'priority Urgent.'
            )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header.")

        for row_number, row in enumerate(reader, start=2):
            try:
                result = classify_complaint(row)

                output_row = dict(row)
                output_row.update(result)

                results.append(output_row)

            except Exception as error:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": (
                        f"Row {row_number} could not be classified safely: "
                        f"{error}."
                    ),
                    "flag": "NEEDS_REVIEW",
                })

    output_fields = list(reader.fieldnames)

    for field in ["category", "priority", "reason", "flag"]:
        if field not in output_fields:
            output_fields.append(field)

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=output_fields,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to test_[city].csv",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV",
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")
