"""
Data parsing utilities for DRM Assessment Tool
Functions to parse and validate pasted question data
"""

import pandas as pd
from config.question_config import QUESTION_MAPPING, THEMATIC_AREAS


def parse_pasted_data(raw_text: str):
    """Parse semicolon-separated question entries in format: Q#,Yes/No,Weight
    Returns dataframe with aggregated scores by thematic area or None if invalid.
    """
    if not raw_text or raw_text.strip() == "":
        return None, "No data provided"
    
    # Split by semicolon to get individual questions
    entries = [e.strip() for e in raw_text.split(";") if e.strip()]
    
    if len(entries) == 0:
        return None, "No question entries provided"
    
    # Parse each question entry
    question_data = {}
    for entry in entries:
        parts = [p.strip() for p in entry.split(",")]
        if len(parts) != 3:
            return None, f"Invalid entry format (expected Q#,Yes/No,Weight): {entry}"
        
        q_id, answer, weight = parts
        
        # Validate question ID
        if q_id not in QUESTION_MAPPING:
            return None, f"Unknown question ID: {q_id}"
        
        # Validate answer
        if answer.lower() not in ["yes", "no", "unknown"]:
            return None, f"Invalid answer for {q_id} (must be Yes, No, or Unknown): {answer}"
        
        # Parse weight
        try:
            weight_val = float(weight)
            if weight_val < 0 or weight_val > 1:
                return None, f"Weight for {q_id} must be between 0 and 1: {weight}"
        except ValueError:
            return None, f"Invalid weight for {q_id}: {weight}"
        
        # Calculate score: if Yes, score = weight; if No or Unknown, score = 0
        score = weight_val if answer.lower() == "yes" else 0
        
        question_data[q_id] = {
            "answer": answer,
            "weight": weight_val,
            "score": score,
            "pillar": QUESTION_MAPPING[q_id]["pillar"],
            "thematic": QUESTION_MAPPING[q_id]["thematic"]
        }
    
    # Aggregate scores by thematic area
    thematic_scores = {}
    thematic_max_scores = {}
    for q_id, data in question_data.items():
        key = (data["pillar"], data["thematic"])
        if key not in thematic_scores:
            thematic_scores[key] = 0
            thematic_max_scores[key] = 0
        thematic_scores[key] += data["score"]
        thematic_max_scores[key] += data["weight"]  # Maximum possible score if all answers were Yes
    
    # Build dataframe with one row per thematic area (normalized scores 0-1)
    records = []
    for area in THEMATIC_AREAS:
        key = (area["pillar"], area["thematic"])
        actual_score = thematic_scores.get(key, 0)
        max_score = thematic_max_scores.get(key, 1)  # Avoid division by zero
        normalized_score = actual_score / max_score if max_score > 0 else 0
        records.append({
            "DRM Pillar": area["pillar"],
            "Thematic Area": area["thematic"],
            "Score": normalized_score
        })
    
    df = pd.DataFrame(records)
    return df, question_data, "Parsed successfully, please wait..."
