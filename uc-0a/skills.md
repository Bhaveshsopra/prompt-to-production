# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint into an allowed category and priority with a reason and review flag.
    input: One complaint row containing the complaint description as text.
    output: A classification containing category, priority, reason, and flag.
    error_handling: If the category is genuinely ambiguous, use category Other and flag NEEDS_REVIEW; never invent a new category.

  - name: batch_classify
    description: Reads a complaint CSV, classifies every complaint using classify_complaint, and writes the results to an output CSV.
    input: Input CSV file containing citizen complaint rows.
    output: Output CSV containing the original data plus category, priority, reason, and flag fields.
    error_handling: If the input CSV is invalid or the complaint description cannot be found, report an error instead of producing unreliable classifications.
