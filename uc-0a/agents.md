# agents.md — UC-0A Complaint Classifier

role: >
  Classify citizen complaints into the fixed UC-0A categories and assign
  an appropriate priority based only on the complaint description.

intent: >
  Produce a consistent output containing an allowed category, priority,
  one-sentence reason citing specific words from the description, and a
  NEEDS_REVIEW flag when the category is genuinely ambiguous.

context: >
  The agent may use only the information contained in each complaint
  description. It must not invent facts, categories, sub-categories, or
  information that is not present in the description.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be exactly one of: Urgent, Standard, Low. Priority must be Urgent when the description contains injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse."
  - "Every output row must include a one-sentence reason citing specific words from the complaint description."
  - "If the category is genuinely ambiguous from the description, use category: Other and flag: NEEDS_REVIEW."
  - "Do not create or use category names outside the allowed category list."
