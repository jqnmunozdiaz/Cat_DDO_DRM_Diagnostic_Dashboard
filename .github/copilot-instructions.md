# Copilot Instructions - DRM Diagnostic Assessment Tool

## Project Overview
This is a **Dash-based single-page web application** for World Bank/GFDRR that evaluates a country's institutional Disaster Risk Management (DRM) system across 6 pillars and 12 thematic areas. Users paste structured data from Excel, and the app generates:
- Circular polar charts (petal diagrams) using matplotlib
- Horizontal progress bars by pillar using Plotly
- Downloadable PNG visualizations

**Key fact**: This is NOT a multi-page dashboard - it's a two-phase linear workflow (data entry → results visualization).

## Architecture & Data Flow

### Core Components
1. **[app.py](app.py)** - Main Dash application (~610 lines)
   - Hard-codes question-to-pillar mapping (QUESTION_MAPPING dict with Q1-Q47)
   - Parses semicolon-delimited Q#,Answer,Weight format from Excel cell B10
   - Manages UI state via `dcc.Store` components and section visibility toggling
   - Implements 6 callbacks for data processing, visualization, and downloads

2. **[scripts/figure_generator.py](scripts/figure_generator.py)** - Circular chart generator
   - Uses matplotlib with 'Agg' backend (non-interactive for web)
   - Creates 12-segment polar bar chart with viridis gradient coloring
   - Returns base64-encoded PNG strings
   - Handles label rotation and positioning for radial layout

3. **[data/DRM System Diagnostic Assessment - Template.xlsx](data/DRM%20System%20Diagnostic%20Assessment%20-%20Template.xlsx)** - Source template
   - Users complete this offline Excel file with 47 Yes/No questions
   - Contains formula in cell B10 that formats data for pasting
   - Structure: Excel answers → `Q#,Answer,Weight;Q#,Answer,Weight;...`

### Data Model
**Input format** (semicolon-separated question entries):
```
Q1,Yes,1;Q2,No,1;Q3,No,0.5;Q4,Yes,0.5;...;Q47,Yes,1
```

Each entry has three parts: `Question ID, Answer (Yes/No), Weight (0-1)`

**Question mapping**: 47 questions (Q1-Q47) map to 12 thematic areas across 6 pillars
- Q1-Q4 → Pillar 1.1 (DRM policies and institutions)
- Q5-Q6 → Pillar 1.2 (Mainstreaming DRM)
- Q7-Q10 → Pillar 2 (Risk Identification)
- Q11-Q27 → Pillar 3 (Risk Reduction - 3 sub-areas)
- Q28-Q37 → Pillar 4 (Preparedness - 3 sub-areas)
- Q38-Q44 → Pillar 5 (Financial Protection - 2 sub-areas)
- Q45-Q47 → Pillar 6 (Resilient Reconstruction)

**Scoring logic**: Answer="Yes" → score = weight; Answer="No" → score = 0. Scores aggregate by thematic area to create "petal length" (max ~4.0 per area).

### Critical Workflows

**Running locally**:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
# App runs on localhost:8050 in debug mode (unless RENDER env var set)
```

**Deploying to Render** (current platform):
- Uses [Procfile](Procfile): `web: gunicorn app:server`
- Python 3.11.7 specified in [runtime.txt](runtime.txt)
- Auto-deploys on git push to main branch
- No environment variables required

**Understanding the calculation logic**:
- Each question has Answer (Yes/No) and Weight (0-1 float)
- Score = Weight if Yes, 0 if No
- Questions aggregate to thematic area scores (sum of individual question scores)
- Thematic area scores < 1.0 flagged as "Below Minimum Standard" (red circle)
- Pillar progress = average of thematic area scores within that pillar

## Dash-Specific Patterns

### Callback Architecture
All callbacks use `prevent_initial_call=True` to avoid execution on page load. Key callbacks:

1. **Data parsing** ([app.py#L315-L330](app.py#L315-L330)): Validates and stores pasted data in `dcc.Store`
2. **Results generation** ([app.py#L332-L511](app.py#L332-L511)): Processes data, generates figures, calculates pillar scores
3. **Section toggling** ([app.py#L576-L585](app.py#L576-L585)): "Back" button clears state and returns to input form
4. **Downloads** ([app.py#L516-L567](app.py#L516-L567)): Converts base64/Plotly figures to PNG downloads

### State Management
- `dcc.Store(id="pasted-data")`: Serialized dict of row values
- `dcc.Store(id="figure-store")`: Base64 image string
- Section visibility controlled via inline style `display: "none"/"block"`
- No database or server-side session storage

### Styling Conventions
- Uses Bootstrap via `dash-bootstrap-components`
- Custom CSS in [assets/css/app.css](assets/css/app.css) (gradient background, card styling)
- Logos loaded from [assets/images/](assets/images/) - requires `wb-full-logo.png` and `gfdrr-logo.png`
- Responsive design with `dbc.Container(fluid=False, maxWidth="1200px")`

## Common Tasks

### Modifying Assessment Structure
1. Edit template Excel file to change pillars/subpillars
2. Update label mappings in [scripts/figure_generator.py#L192-L204](scripts/figure_generator.py#L192-L204) for display names
3. Adjust `title_texts` list in [scripts/figure_generator.py#L156](scripts/figure_generator.py#L156) if pillar count changes

### Changing Visualization Colors
- **Polar chart gradient**: [scripts/figure_generator.py#L109](scripts/figure_generator.py#L109) - uses matplotlib's 'viridis' colormap
- **Pillar progress bars**: [app.py#L439-L448](app.py#L439-L448) - red (<25%), orange (<50%), yellow (<75%), blue (≥75%)
- **Reference circles**: [scripts/figure_generator.py#L239-L242](scripts/figure_generator.py#L239-L242) - red (nascent), orange (emerging), blue (established), green (mature)

### Adding/Removing Questions
1. Update template Excel file to add/remove question rows
2. Update `QUESTION_MAPPING` dict in [app.py](app.py) to map new Q# to pillar/thematic
3. Update `THEMATIC_AREAS` list if adding new thematic areas
4. No changes to parsing logic needed - it auto-processes all Q# entries

### Debugging Data Parsing Issues
- Check paste format in browser console - must have `;` entry delimiters and `,` field delimiters
- Each entry must be exactly 3 parts: `Q#,Yes/No,Weight`
- Validation errors shown via `html.Div(className="alert alert-danger")` below paste textarea
- Question ID must exist in `QUESTION_MAPPING` (Q1-Q47)
- Answer must be "Yes" or "No" (case-insensitive)
- Weight must be valid float between 0 and 1

## Dependencies & Compatibility

**Critical versions** (from [requirements.txt](requirements.txt)):
- `dash>=2.14.0,<3.0.0` - Callback signatures changed in v2.14
- `kaleido>=0.2.1` - Required for Plotly figure-to-image conversion (used in pillar download)
- `matplotlib>=3.8.0` - 'Agg' backend for headless rendering

**Why gunicorn**: Dash's built-in Flask server not production-ready; gunicorn provides WSGI server for Render deployment.

## Known Limitations
- No authentication or user accounts
- No data persistence (results lost on page refresh)
- Single concurrent user per session (no multi-user collaboration)
- Excel template must be downloaded separately (not embedded)
- Paste format is brittle - users must copy exact cell E7 content
- Old data files in `data/_old/` are ignored (use for reference only)

## Testing Approach
- Use "Show Example" button to load pre-formatted sample data
- Example data: 47-question string in correct format
- Verify charts render with: 12 petals (thematic areas), 6 group labels (pillars), 4 reference circles
- Test edge cases: missing questions (default to 0), invalid Q# (error), non-Yes/No answers (error), weights outside 0-1 (error)
- Sample test: `Q1,Yes,1;Q2,No,1` should aggregate to score of 1.0 for Pillar 1.1

## Anti-Patterns to Avoid
- Don't create multi-page navigation - this is intentionally single-page with section toggling
- Don't store file uploads - data comes as text paste only
- Don't add database dependencies - tool designed for stateless deployment
- Don't use `dash.callback_context` - prefer explicit Input/State declarations
- Don't modify [scripts/Example_Summary_Figure_clean.py](scripts/Example_Summary_Figure_clean.py) - it's legacy reference code

## Quick Reference: File Roles
| File | Purpose | Modify When |
|------|---------|-------------|
| [app.py](app.py) | UI & callbacks | Changing workflow, adding features |
| [scripts/figure_generator.py](scripts/figure_generator.py) | Polar chart logic | Adjusting visualization design |
| [data/DRM System Diagnostic Assessment - Template.xlsx](data/DRM%20System%20Diagnostic%20Assessment%20-%20Template.xlsx) | User-facing template | Changing pillars/questions |
| [assets/css/app.css](assets/css/app.css) | Custom styling | UI appearance changes |
| [Procfile](Procfile) | Deployment config | Switching WSGI server |
| [requirements.txt](requirements.txt) | Dependencies | Adding packages |
