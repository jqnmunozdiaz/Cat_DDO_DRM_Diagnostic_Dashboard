# Copilot Instructions - DRM Diagnostic Assessment Tool

## Project Overview
This is a **Dash-based single-page web application** for World Bank/GFDRR that evaluates a country's institutional Disaster Risk Management (DRM) system across 6 pillars and 12 thematic areas. Users paste structured data from Excel, and the app generates:
- Circular polar charts (petal diagrams) using **Plotly**
- Horizontal progress bars by pillar using Plotly
- AI-generated summaries for each thematic area
- Downloadable PNG visualizations

**Key fact**: This is NOT a multi-page dashboard - it's a two-phase linear workflow (data entry → results visualization).

**Live demo**: https://cat-ddo-drm-diagnostic-dashboard-129737065802.us-central1.run.app/

## Architecture & Data Flow

### Core Components

```
Cat_DDO_DRM_Diagnostic_Dashboard/
├── app.py                      # Main Dash app entry point (~35 lines)
├── callbacks/                  # Dash callback handlers
│   ├── __init__.py             # Registers all callbacks via register_callbacks(app)
│   ├── data_callbacks.py       # Data parsing, figure generation, results
│   ├── download_callbacks.py   # PNG download functionality
│   └── ui_callbacks.py         # Section toggling (back button)
├── layouts/                    # UI layout components
│   ├── header.py               # Logo header with WB/GFDRR branding
│   ├── input_section.py        # Data paste form, country dropdown
│   ├── main_layout.py          # Combines header + sections
│   └── results_section.py      # Petal chart, pillar bars, summaries
├── utils/                      # Helper utilities
│   ├── data_parser.py          # parse_pasted_data() - validates Q#,Yes/No,Weight
│   └── thematic_helpers.py     # LLM summary loading, answer indicators
├── config/
│   └── question_config.py      # THEMATIC_AREA_QUESTIONS, QUESTION_MAPPING
├── scripts/                    # Visualization generators
│   ├── petal_chart_figure_generator.py  # Plotly polar bar chart
│   └── pillar_chart.py         # Plotly horizontal progress bars
├── LLM/                        # Pre-generated thematic summaries (JSON)
│   ├── 1.1. DRM policies and institutions.json
│   ├── ... (one per thematic area)
│   └── questions_mapping.json
├── data/
│   └── DRM System Diagnostic Assessment - Template.xlsx
└── assets/
    ├── css/app.css             # Custom styling
    └── images/                 # WB/GFDRR logos
```

### Data Model
**Input format** (semicolon-separated question entries from Excel cell B10):
```
Q1,Yes,1;Q2,No,1;Q3,No,0.5;Q4,Yes,0.5;...;Q47,Yes,1
```

Each entry: `Question ID, Answer (Yes/No), Weight (0-1)`

**Question mapping**: 47 questions (Q1-Q47) map to 12 thematic areas across 6 pillars:
- Q1-Q4 → Pillar 1.1 (DRM policies and institutions)
- Q5-Q6 → Pillar 1.2 (Mainstreaming DRM)
- Q7-Q10 → Pillar 2 (Risk Identification)
- Q11-Q27 → Pillar 3 (Risk Reduction - 3 sub-areas)
- Q28-Q37 → Pillar 4 (Preparedness - 3 sub-areas)
- Q38-Q44 → Pillar 5 (Financial Protection - 2 sub-areas)
- Q45-Q47 → Pillar 6 (Resilient Reconstruction)

**Scoring logic**: Answer="Yes" → score = weight; Answer="No" → score = 0. Scores are normalized (0-1) per thematic area. Areas with score < 0.25 flagged as "Below Minimum Standard".

### Critical Workflows

**Running locally**:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
# App runs on localhost:8050 in debug mode (unless RENDER env var set)
```

**Deploying to Google Cloud Run** (current platform):
- Uses [Dockerfile](Dockerfile) for containerization
- App Engine config in [app.yaml](app.yaml)
- Auto-deploys on git push to main branch
- No environment variables required

## Dash-Specific Patterns

### Callback Architecture
All callbacks use `prevent_initial_call=True`. Callbacks are registered in `callbacks/__init__.py`:

1. **Data parsing** (`data_callbacks.py`): Validates paste → stores in `dcc.Store("pasted-data")`
2. **Results generation** (`data_callbacks.py`): Generates petal chart, pillar bars, themed summaries
3. **Section toggling** (`ui_callbacks.py`): "Back" button shows input, hides results
4. **Downloads** (`download_callbacks.py`): Converts Plotly figures to PNG

### State Management
- `dcc.Store(id="pasted-data")`: Serialized dict with parsed dataframe and question answers
- `dcc.Store(id="figure-store")`: Plotly figure dict for download
- Section visibility controlled via inline style `display: "none"/"block"`
- No database or server-side session storage

### Styling Conventions
- Uses Bootstrap via `dash-bootstrap-components`
- Custom CSS in [assets/css/app.css](assets/css/app.css)
- Font Awesome icons via CDN
- Responsive design with `dbc.Container`

## Common Tasks

### Modifying Question Configuration
Edit [config/question_config.py](config/question_config.py):
```python
THEMATIC_AREA_QUESTIONS = [
    {"pillar": "1. Legal and Institutional DRM Framework", 
     "thematic": "1.1. DRM policies and institutions", 
     "questions": "Q1-Q4"},
    # Add/modify entries here...
]
```
The `QUESTION_MAPPING` dict is auto-generated from this list.

### Changing Visualization Colors
- **Petal chart**: [scripts/petal_chart_figure_generator.py](scripts/petal_chart_figure_generator.py) - uses Plotly
- **Pillar progress bars**: [scripts/pillar_chart.py](scripts/pillar_chart.py) - color thresholds by score level
- **Reference circles**: Dashed lines at 0.25 (Nascent), 0.50 (Emerging), 0.75 (Established), 1.0 (Mature)

### Adding/Editing Thematic Summaries
Pre-generated LLM summaries stored in [LLM/](LLM/) folder as JSON files. Each file contains text keyed by answer pattern (e.g., "Yes_Yes_No_Yes"). Edit these files to change summary text. Summaries support `{country}` placeholder.

### Debugging Data Parsing Issues
- Check paste format - must have `;` entry delimiters and `,` field delimiters
- Each entry must be exactly 3 parts: `Q#,Yes/No,Weight`
- Validation errors shown in alert below paste textarea
- Question ID must exist in `QUESTION_MAPPING` (Q1-Q47)
- Answer must be "Yes" or "No" (case-insensitive)
- Weight must be valid float between 0 and 1

## Dependencies & Compatibility

**Key packages** (from [requirements.txt](requirements.txt)):
- `dash>=2.14.0,<3.0.0` - Callback signatures changed in v2.14
- `plotly>=5.18.0` - For all chart visualizations
- `pandas>=2.1.0` - Data manipulation
- `dash-bootstrap-components>=1.5.0` - UI components
- `gunicorn>=21.2.0` - WSGI server for production

**Why gunicorn**: Dash's built-in Flask server not production-ready; gunicorn provides WSGI server for deployment.

## Known Limitations
- No authentication or user accounts
- No data persistence (results lost on page refresh)
- Single concurrent user per session (no multi-user collaboration)
- Excel template must be downloaded separately (not embedded)
- Paste format is brittle - users must copy exact cell B10 content

## Testing Approach
- Use "Show Example" button to load pre-formatted sample data
- Example data: 47-question string in correct format
- Verify charts render with: 12 petals (thematic areas), 6 pillars, 4 reference circles
- Test edge cases: missing questions (default to 0), invalid Q# (error), non-Yes/No answers (error), weights outside 0-1 (error)

## Anti-Patterns to Avoid
- Don't create multi-page navigation - this is intentionally single-page with section toggling
- Don't store file uploads - data comes as text paste only
- Don't add database dependencies - tool designed for stateless deployment
- Don't modify [scripts/Example_Summary_Figure_clean.py](scripts/Example_Summary_Figure_clean.py) - it's legacy reference code

## Quick Reference: File Roles
| File/Folder | Purpose | Modify When |
|-------------|---------|-------------|
| [app.py](app.py) | Entry point, app init | Rarely needed |
| [callbacks/](callbacks/) | All Dash callbacks | Adding features, changing workflow |
| [layouts/](layouts/) | UI components | Changing UI structure |
| [config/question_config.py](config/question_config.py) | Question mapping | Changing pillars/questions |
| [scripts/petal_chart_figure_generator.py](scripts/petal_chart_figure_generator.py) | Petal chart logic | Adjusting chart design |
| [scripts/pillar_chart.py](scripts/pillar_chart.py) | Pillar bar chart | Adjusting bar design |
| [LLM/](LLM/) | Thematic summaries | Editing AI-generated text |
| [utils/](utils/) | Helper functions | Changing parsing/validation |
| [assets/css/app.css](assets/css/app.css) | Custom styling | UI appearance changes |
| [data/](data/) | Excel template | Changing template |
