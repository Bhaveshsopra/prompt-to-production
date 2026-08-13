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


def classify_complaint(row: dict) -> dict:
    """
    Classify one complaint row.

    Returns:
        complaint_id, category, priority, reason, flag
    """

    complaint_id = row.get("complaint_id", "")

    # Find the complaint description column.
    description = (
        row.get("description")
        or row.get("complaint")
        or row.get("text")
        or row.get("complaint_description")
        or ""
    )

    description = str(description).strip()

    # Handle missing/null descriptions safely.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": 'No complaint description was provided.',
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Severity always overrides normal priority.
    if any(keyword in text for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Category classification using only allowed categories.
    if "pothole" in text:
        category = "Pothole"

    elif any(word in text for word in [
        "flood",
        "flooding",
        "waterlogged",
        "water logging",
    ]):
        category = "Flooding"

    elif any(word in text for word in [
        "streetlight",
        "street light",
        "lamp post",
    ]):
        category = "Streetlight"

    elif any(word in text for word in [
        "garbage",
        "waste",
        "trash",
        "rubbish",
    ]):
        category = "Waste"

    elif any(word in text for word in [
        "noise",
        "loud music",
        "loudspeaker",
    ]):
        category = "Noise"

    elif any(word in text for word in [
        "road damage",
        "damaged road",
        "cracked road",
    ]):
        category = "Road Damage"

    elif any(word in text for word in [
        "heritage",
        "monument",
        "historical building",
    ]):
        category = "Heritage Damage"

    elif any(word in text for word in [
        "heatwave",
        "heat wave",
        "extreme heat",
        "heat hazard",
    ]):
        category = "Heat Hazard"

    elif any(word in text for word in [
        "drain",
        "drainage",
        "blocked drain",
    ]):
        category = "Drain Blockage"

    else:
        category = "Other"

    # Genuinely unknown category requires review.
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    # Reason cites specific words from the description.
    reason = f'Classification based on the complaint description: "{description}".'

    # Final enforcement checks.
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
    """
    Read input CSV, classify every row, and write results.

    Bad or incomplete rows do not stop the entire batch.
    """

    results = []

    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header.")

        for row_number, row in enumerate(reader, start=2):
            try:
                result = classify_complaint(row)

                # Preserve the original row.
                output_row = dict(row)

                # Add required classification fields.
                output_row.update(result)

                results.append(output_row)

            except Exception as error:
                # Do not crash the complete batch.
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row {row_number} could not be classified safely: {error}.",
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
