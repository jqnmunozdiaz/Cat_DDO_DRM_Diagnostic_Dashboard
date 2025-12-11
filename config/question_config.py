"""
Configuration file for DRM Assessment question mapping
Define question ranges for each thematic area and generate mappings
"""

# ============================================================================
# CONFIGURE QUESTION RANGES FOR EACH THEMATIC AREA
# ============================================================================
# Simply specify the question range for each thematic area using format: "Q1-Q4"
THEMATIC_AREA_QUESTIONS = [
    {"pillar": "1. Legal and Institutional DRM Framework", "thematic": "1.1. DRM policies and institutions", "questions": "Q1-Q4"},
    {"pillar": "1. Legal and Institutional DRM Framework", "thematic": "1.2. Mainstreaming DRM into national and sectoral development plans", "questions": "Q5-Q6"},
    {"pillar": "2. Risk Identification", "thematic": "Risk identification", "questions": "Q7-Q10"},
    {"pillar": "3. Risk Reduction", "thematic": "3.1. Territorial and urban planning", "questions": "Q11-Q14"},
    {"pillar": "3. Risk Reduction", "thematic": "3.2. Public investment at the central level", "questions": "Q15-Q17"},
    {"pillar": "3. Risk Reduction", "thematic": "3.3. Sector-specific risk reduction measures", "questions": "Q18-Q27"},
    {"pillar": "4. Preparedness", "thematic": "4.1. Early warning systems", "questions": "Q28-Q30"},
    {"pillar": "4. Preparedness", "thematic": "4.2. Emergency preparedness and response", "questions": "Q31-Q34"},
    {"pillar": "4. Preparedness", "thematic": "4.3. Adaptive social protection", "questions": "Q35-Q37"},
    {"pillar": "5. Financial Protection", "thematic": "5.1. Fiscal risk management", "questions": "Q38-Q41"},
    {"pillar": "5. Financial Protection", "thematic": "5.2. DRF strategies and instruments", "questions": "Q42-Q44"},
    {"pillar": "6. Resilient Reconstruction", "thematic": "Resilient reconstruction", "questions": "Q45-Q47"},
]


def parse_question_range(range_str):
    """Parse question range string like 'Q1-Q4' into list of question IDs"""
    start, end = range_str.split('-')
    start_num = int(start.strip()[1:])  # Remove 'Q' prefix
    end_num = int(end.strip()[1:])
    return [f"Q{i}" for i in range(start_num, end_num + 1)]


# Generate QUESTION_MAPPING from the ranges above
QUESTION_MAPPING = {}
for area in THEMATIC_AREA_QUESTIONS:
    question_ids = parse_question_range(area["questions"])
    for q_id in question_ids:
        QUESTION_MAPPING[q_id] = {
            "pillar": area["pillar"],
            "thematic": area["thematic"]
        }

# Build thematic area template structure (for DataFrame construction)
THEMATIC_AREAS = [
    {"pillar": area["pillar"], "thematic": area["thematic"]}
    for area in THEMATIC_AREA_QUESTIONS
]
