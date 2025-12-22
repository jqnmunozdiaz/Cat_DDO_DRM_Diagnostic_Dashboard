"""
Thematic helpers - functions for generating indicators and loading summaries
"""
import json
from pathlib import Path
from config.question_config import THEMATIC_AREA_QUESTIONS, parse_question_range


def generate_answer_indicator(question_data, thematic_area):
    """Generate binary indicator string (e.g., '1010') for a thematic area based on answers"""
    # Find the question range for this thematic area
    for area_config in THEMATIC_AREA_QUESTIONS:
        if area_config["thematic"] == thematic_area:
            question_ids = parse_question_range(area_config["questions"])
            # Generate binary string: 1 for Yes, 0 for No
            indicator = ""
            for q_id in question_ids:
                if q_id in question_data:
                    indicator += "1" if question_data[q_id]["answer"].lower() == "yes" else "0"
                else:
                    indicator += "0"  # Default to No if question not found
            return indicator
    return None


def load_thematic_summary(thematic_area, indicator):
    """Load LLM-generated summary from JSON file based on thematic area and answer indicator"""
    try:
        # Special handling for 3.3 which has 10 questions split into 2 parts
        if thematic_area == "3.3. Sector-specific risk reduction measures" and len(indicator) == 10:
            # Split indicator into two parts: first 5 and last 5 questions
            indicator_part1 = indicator[:5]
            indicator_part2 = indicator[5:]
            
            # Load from part1 JSON
            json_file_part1 = Path("LLM") / f"{thematic_area}_part1.json"
            summary_part1 = "Summary for part 1 will be available soon."
            if json_file_part1.exists():
                with open(json_file_part1, 'r', encoding='utf-8') as f:
                    summaries_part1 = json.load(f)
                summary_part1 = summaries_part1.get(indicator_part1, "Summary content for this response pattern will be available soon.")
            
            # Load from part2 JSON
            json_file_part2 = Path("LLM") / f"{thematic_area}_part2.json"
            summary_part2 = "Summary for part 2 will be available soon."
            if json_file_part2.exists():
                with open(json_file_part2, 'r', encoding='utf-8') as f:
                    summaries_part2 = json.load(f)
                summary_part2 = summaries_part2.get(indicator_part2, "Summary content for this response pattern will be available soon.")
            
            # Combine summaries
            return f"{summary_part1} {summary_part2}"
        
        # Regular handling for other thematic areas
        # Construct file path
        json_file = Path("LLM") / f"{thematic_area}.json"
        
        if not json_file.exists():
            return "Summary content will be available soon."
        
        # Load JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            summaries = json.load(f)
        
        # Get summary for this indicator pattern
        summary = summaries.get(indicator, "Summary content for this response pattern will be available soon.")
        return summary
    except Exception as e:
        return f"Error loading summary: {str(e)}"
