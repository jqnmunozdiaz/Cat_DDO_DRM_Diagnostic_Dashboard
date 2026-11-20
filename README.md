# DRM Policy Diagnostic Tool

A web dashboard that evaluates a country's Disaster Risk Management (DRM) policy and institutional framework across six pillars and twelve thematic areas.

**Live app:** https://cat-ddo-drm-diagnostic-dashboard-129737065802.us-central1.run.app

## How it works

1. Download and fill in the questionnaire (`data/DRM Rapid Screening Tool - Questionnaire.xlsx`).
2. Paste the results string from the questionnaire into the app.
3. The app shows a petal chart by thematic area, a progress chart by pillar, and short text summaries for each area. You can save the results as a PDF.

## Run it locally

Requires Python 3.11+.

```bash
git clone https://github.com/jqnmunozdiaz/Cat_DDO_DRM_Diagnostic_Dashboard.git
cd Cat_DDO_DRM_Diagnostic_Dashboard
pip install -r requirements.txt
python app.py
```

Then open http://localhost:8050.

## Project structure

- `app.py`: entry point.
- `layouts/`: page sections (header, input, results).
- `callbacks/`: data processing, charts and downloads.
- `config/`: question-to-pillar mapping and constants.
- `utils/`: input parsing and summary helpers.
- `scripts/`: chart generators, plus the script that extracts questions from the Excel file for the LLM summaries.
- `LLM/`: pre-generated text summaries for each thematic area.
- `data/`: the questionnaire users fill in.
- `assets/`: CSS, logos, framework image and the methodological note (PDF and Word).

## Deployment

Every push to `main` rebuilds the [Dockerfile](Dockerfile) and deploys it to Google Cloud Run (project `drm-diagnostic-tool`, service `cat-ddo-drm-diagnostic-dashboard`, region `us-central1`).

## Credits

Developed by the World Bank Group and the Global Facility for Disaster Reduction and Recovery (GFDRR).
