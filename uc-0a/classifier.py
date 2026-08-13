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

    priority = "Urgent" if severity_match else "Standard"

    category = "Other"
    category_match = None

    # More specific categories are checked first.
    rules = [
        (
            "Heritage Damage",
            [
                "heritage",
                "historic",
                "historical",
                "heritage stone",
                "heritage zone",
                "heritage precinct",
            ],
        ),
        (
            "Pothole",
            [
                "pothole",
            ],
        ),
        (
            "Flooding",
            [
                "flood",
                "flooding",
                "waterlogged",
                "water logging",
                "inaccessible due to rain",
            ],
        ),
        (
            "Noise",
            [
                "noise",
                "loud music",
                "loudspeaker",
                "music past midnight",
                "wedding band",
                "band playing",
                "amplifier",
                "amplifiers",
            ],
        ),
        (
            "Streetlight",
            [
                "streetlight",
                "street light",
                "lamp post",
                "darkness",
                "lights out",
                "substation tripped",
            ],
        ),
        (
            "Waste",
            [
                "garbage",
                "waste",
                "trash",
                "rubbish",
                "dumped",
                "overflowing bins",
            ],
        ),
        (
            "Road Damage",
            [
                "road damage",
                "damaged road",
                "cracked road",
                "road surface",
                "road surface cracked",
                "road surface buckled",
                "buckled",
                "cracked",
                "sinking",
                "subsided",
                "broken footpath",
                "footpath broken",
                "footpath tiles",
                "upturned",
                "broken and sinking",
            ],
        ),
        (
            "Heat Hazard",
            [
                "heatwave",
                "heat wave",
                "extreme heat",
                "heat hazard",
            ],
        ),
        (
            "Drain Blockage",
            [
                "blocked drain",
                "drain blocked",
                "drain blockage",
                "blocked drainage",
                "manhole blocked",
            ],
        ),
    ]

    for possible_category, keywords in rules:
        match = find_match(text, keywords)

        if match:
            category = possible_category
            category_match = match
            break

    if category == "Other":
        flag = "NEEDS_REVIEW"

        reason = (
            f'No allowed category could be determined confidently from '
            f'the description: "{description}".'
        )

    else:
        flag = ""

        reason = (
            f'The phrase "{category_match}" supports the category '
            f'"{category}".'
        )

        if severity_match:
            reason += (
                f' The severity keyword "{severity_match}" makes the '
                f'priority "Urgent".'
            )

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

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
