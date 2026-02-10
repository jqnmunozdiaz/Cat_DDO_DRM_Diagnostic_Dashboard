# DRM Diagnostic Assessment Tool

This tool is a web-based dashboard developed to support countries in assessing and strengthening their institutional setting for Disaster Risk Management (DRM) across six critical pillars:

1. **Legal and Institutional DRM Framework**
2. **Risk Identification**
3. **Risk Reduction**
4. **Preparedness**
5. **Financial Protection**
6. **Resilient Reconstruction**

## Live Demo

https://cat-ddo-drm-diagnostic-dashboard-129737065802.us-central1.run.app/

## Features

- **Assessment Questionnaire**: Paste DRM assessment data from Excel template
- **Petal Chart Visualization**: Circular polar chart showing progress across thematic areas
- **Pillar Progress Bars**: Aggregated results by DRM pillar 
- **AI-Generated Summaries**: LLM-powered analysis of each thematic area
- **Export to PNG**: Download charts for reports and presentations

## Project Structure

```
Cat_DDO_DRM_Diagnostic_Dashboard/
├── app.py                      # Main Dash application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container config
├── app.yaml                    # Google Cloud App Engine config
├── callbacks/                  # Dash callback handlers
│   ├── data_callbacks.py
│   ├── download_callbacks.py
│   └── ui_callbacks.py
├── layouts/                    # UI layout components
│   ├── header.py
│   ├── input_section.py
│   ├── main_layout.py
│   └── results_section.py
├── utils/                      # Helper utilities
│   ├── data_parser.py
│   └── thematic_helpers.py
├── config/
│   └── question_config.py      # Assessment configuration
├── assets/
│   ├── css/                    # Custom styling
│   ├── images/                 # Logos and images
│   └── documents/              # Supporting documents
├── data/
│   └── DRM System Diagnostic Assessment - Template.xlsx
└── scripts/                    # Development scripts
```

## Development

Run the application locally with app.py after cloning and installing dependencies (requirements.txt).
Google Cloud automatically redeploys when changes are pushed to the main branch.

## Contact

jmunozdiaz@worldbank.org
jqnmunozdiaz@gmail.com

