"""
DRM Diagnostic Assessment Tool - Dash Application
Simple one-page dashboard for evaluating country's institutional setting for DRM
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from scripts.figure_generator import generate_figure
import base64
import os
import re

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Load the template CSV to get structure
template_df = pd.read_csv("data/DRM_system_assessment_template_filled_example.csv")

# Extract value columns (all columns except DRM Pillar and Thematic Area)
value_columns = [col for col in template_df.columns if col not in ["DRM Pillar", "Thematic Area"]]

def parse_pasted_data(raw_text: str):
    """Parse semicolon-separated rows with comma-separated columns.
    Returns dataframe aligned to template columns or None if invalid.
    Expected header must include the value column names matching template.
    """
    if not raw_text or raw_text.strip() == "":
        return None, "No data provided"
    # Split rows by semicolon
    rows = [r.strip() for r in raw_text.split(";") if r.strip()]
    if len(rows) < 2:
        return None, "Not enough rows (need header + at least one data row)"
    header = rows[0].split(",")
    # Normalize header spacing
    header = [h.strip() for h in header]
    required_first_two = ["DRM Pillar", "Thematic Area"]
    if header[0:2] != required_first_two:
        return None, "Header must start with 'DRM Pillar,Thematic Area'"
    # Map remaining headers to template value columns by approximate match
    template_map = {}
    remaining_headers = header[2:]
    # Build a lowercase simplified map of template value columns
    simplified_template = {re.sub(r'[^a-z0-9]', '', c.lower()): c for c in value_columns}
    for h in remaining_headers:
        key = re.sub(r'[^a-z0-9]', '', h.lower())
        if key in simplified_template:
            template_map[h] = simplified_template[key]
        else:
            return None, f"Unrecognized header column: {h}"
    # Ensure all template value columns are present (strict)
    if set(template_map.values()) != set(value_columns):
        return None, "Header value columns do not match required template columns"
    # Parse data rows
    data_records = []
    for r in rows[1:]:
        cols = [c.strip() for c in r.split(",")]
        if len(cols) != len(header):
            return None, f"Row has {len(cols)} columns, expected {len(header)}: {r}"
        record = {
            "DRM Pillar": cols[0],
            "Thematic Area": cols[1]
        }
        # Map each remaining value
        for original_header, raw_val in zip(remaining_headers, cols[2:]):
            target_col = template_map[original_header]
            v = raw_val.strip()
            if v == "" or v.lower() in ["na", "nan", "-"]:
                record[target_col] = ""
            else:
                try:
                    num = float(v)
                    # Clamp 0-1
                    num = max(0, min(1, num))
                    record[target_col] = num
                except ValueError:
                    record[target_col] = ""
        data_records.append(record)
    # Build dataframe
    df = pd.DataFrame(data_records)
    return df, "Parsed successfully"

# App layout
app.layout = dbc.Container([
    # Header with logos
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(src="/assets/images/wb-full-logo.png", height="60px", className="me-3"),
                html.Img(src="/assets/images/gfdrr-logo.png", height="60px")
            ], style={"display": "flex", "alignItems": "center", "justifyContent": "center", "marginBottom": "20px", "gap": "20px"})
        ], width=12)
    ]),
    
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("DRM Diagnostic Assessment Tool", className="mb-2 text-center"),
            html.P(
                "Evaluate your country's institutional setting for Disaster Risk Management across six critical pillars.",
                className="text-center text-muted mb-4 lead"
            ),
            dbc.Alert(
                "Prototype: this will be updated following test cases. Your feedback is welcomed.",
                color="info",
                className="mb-4 text-center"
            )
        ], width=12)
    ]),
    
    # Main content
    dbc.Row([
        dbc.Col([
            # Contextual information
            html.Div([
                html.P([
                    "Disaster risk is a development challenge that must be addressed through multisectoral policies. Unlike traditional sectors, Disaster Risk Management (DRM) cuts across infrastructure sectors, such as energy, water, transport, urban development, as well as socioenvironmental sectors, such as education, health, social protection and environmental management. As a result, disaster risk has direct implication for economic growth, fiscal stability and jobs. While policies for managing the immediate impacts of disasters are vital, a more comprehensive approach is needed to reduce underlying risks. A sound DRM policy framework therefore requires a system-perspective approach to effectively enable disaster resilience."
                ], className="text-muted"),
                html.P([
                    "Recognizing this cross-sectoral nature, the World Bank DRM framework provides a structured approach to evaluate a country's DRM policy framework. Drawing on practical country experiences and global good practices, this framework was first proposed in \"The Sendai Report\" (Ghesquiere et al. 2012) and is aligned with the Sendai Framework for DRR. It is organized around six essential components of DRM encompassing not only legal and institutional DRM frameworks, but also key policy dimensions related to risk information, risk reduction at the sectoral and territorial level, EP&R, financial protection and resilient recovery. This standardized framework helps assess the maturity of a country's DRM policy framework and identify potential gaps across critical resilience-building dimensions. In doing so, it supports the identification of priority policy actions to shift from reactive disaster response toward a more strategic and forward-looking approach to managing disaster and climate-related risks."
                ], className="text-muted")
            ], className="mb-4"),
            
            # Section 1: Input Form
            html.Div([
                html.H3("Assessment Data", className="mb-4"),
                
                # Download template button
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Download Diagnostic Questionnaire", id="download-template-button", color="info", outline=True, className="mb-3"),
                        dcc.Download(id="download-template")
                    ], width=12)
                ]),
                
                # Paste area to bulk-populate the table
                html.Div([
                    html.Label("Please paste the data from cell D7 of your spreadsheet after completing the diagnostic:", className="form-label fw-semibold"),
                    dcc.Textarea(id="paste-input", placeholder="",
                                  style={"width": "100%", "height": "110px", "fontFamily": "monospace"}),
                    html.Div([
                        dbc.Button("See Results", id="paste-apply", color="primary", className="mt-2 me-2"),
                        dbc.Button("Show Example", id="example-button", color="info", outline=True, className="mt-2")
                    ]),
                    html.Div(id="paste-feedback", className="mt-2"),

                    # Collapsible example section
                    dbc.Collapse(
                        [
                            html.P(
                                "Enter the text in cell D7 following the required format. You can copy and paste the example to proceed.",
                                className="form-text text-muted mb-2"
                            ),
                            dbc.Card(dbc.CardBody([
                                html.Pre(
                                    "DRM Pillar,Thematic Area,Legal and institutional set up,Intermediary DRM outputs,Key DRM achievements,Policy enablers;\n"
                                    "Legal and Institutional DRM Framework,DRM policies and institutions,1,1,1,0.33;\n"
                                    "Legal and Institutional DRM Framework,Mainstreaming DRM into national and sectoral development plans,1,0,1,0;\n"
                                    "Risk Identification,Risk identification,1,0.5,1,1;\n"
                                    "Risk Reduction,Territorial and urban planning,1,1,1,0.5;\n"
                                    "Risk Reduction,Public investment at the central level,1,1,1,0;\n"
                                    "Risk Reduction,Sector-specific risk reduction measures,1,0,0,0;\n"
                                    "Preparedness,Early warning systems,1,1,1,1;\n"
                                    "Preparedness,Emergency preparedness and response,1,1,0.5,1;\n"
                                    "Preparedness,Adaptive social protection,0,0,0,0;\n"
                                    "Financial Protection,Fiscal risk management,0,1,1,1;\n"
                                    "Financial Protection,DRF strategies and instruments,1,0,0,1;\n"
                                    "Resilient Reconstruction,Resilient reconstruction,1,0,1,0",
                                    style={"whiteSpace": "pre-wrap", "fontFamily": "monospace", "fontSize": "0.85rem"}
                                )
                            ]))
                        ],
                        id="example-collapse",
                        is_open=False,
                        className="mt-2"
                    )
                ], className="mb-4"),
            ], id="section-1", className="section-1 p-4 mb-5 border rounded bg-light"),

            # Section 2: Results (hidden initially)
            html.Div([
                # Title with Back button on the right
                dbc.Row([
                    dbc.Col([
                        html.H3("Assessment Results", className="mb-0")
                    ], width="auto"),
                    dbc.Col([
                        dbc.Button("Back", id="back-button", color="secondary", outline=True, size="sm")
                    ], width="auto", className="ms-auto")
                ], align="center", className="mb-4"),
                
                # Analysis text
                html.Div(id="analysis-text", className="mb-4"),
                
                # Figure container
                html.Div(
                    id="figure-container",
                    className="text-center mb-4"
                ),
                
                # Download buttons
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Download Figure",
                            id="download-button",
                            color="success",
                            outline=True,
                            className="me-2"
                        ),
                        dcc.Download(id="download-image")
                    ], width=12)
                ], className="mt-4")
            ], id="results-section", className="section-2 p-4 border rounded bg-light", style={"display": "none"}),
            
        ], width=12, lg=10)
    ], justify="center"),
    
    # Hidden div to store the current figure
    dcc.Store(id="figure-store"),
    # Hidden store for pasted data applied to table
    dcc.Store(id="pasted-data"),
    
], fluid=False, style={"maxWidth": "1200px"})

# Callback: parse pasted data and store serialized result
@app.callback(
    Output("pasted-data", "data"),
    Output("paste-feedback", "children"),
    Input("paste-apply", "n_clicks"),
    State("paste-input", "value"),
    prevent_initial_call=True
)
def handle_paste(n_clicks, raw_text):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    df_parsed, status = parse_pasted_data(raw_text or "")
    if df_parsed is None:
        return dash.no_update, html.Div(status, className="alert alert-danger")
    # Serialize parsed dataframe to the structure expected by generate_table
    rows_dict = {}
    for i in range(len(df_parsed)):
        row_map = {}
        for col in value_columns:
            if col in df_parsed.columns:
                val = df_parsed.iloc[i][col]
                if val == "" or pd.isna(val):
                    continue
                try:
                    row_map[col] = float(val)
                except Exception:
                    continue
        rows_dict[str(i)] = row_map
    serialized = {"rows": rows_dict}
    return serialized, html.Div(status, className="alert alert-success")

# Callback to generate results on paste or See Results button
@app.callback(
    [Output("section-1", "style"),
     Output("results-section", "style"),
     Output("figure-store", "data"),
     Output("figure-container", "children"),
     Output("analysis-text", "children")],
    Input("paste-apply", "n_clicks"),
    Input("pasted-data", "data"),
    prevent_initial_call=True
)
def update_results(n_clicks, pasted_data):
    """Process pasted data and generate figure"""
    if not pasted_data or "rows" not in pasted_data:
        raise dash.exceptions.PreventUpdate
    
    # Build dataframe from pasted store / Prepare table data for the input form, empty
    df = template_df.copy() 
    for col in value_columns:
        df[col] = ""
    
    for idx_str, colmap in pasted_data["rows"].items():
        try:
            row_idx = int(idx_str)
        except Exception:
            continue
        if 0 <= row_idx < len(df):
            for col_name, value in colmap.items():
                if col_name in value_columns:
                    try:
                        num_value = float(value)
                        num_value = max(0, min(1, num_value))
                    except (ValueError, TypeError):
                        num_value = 0
                    df.at[row_idx, col_name] = num_value
    
    # Analyze results - find areas below minimum standard (1.0)
    below_minimum = []
    
    # Group by pillar and calculate total scores
    df_analysis = df.copy()
    df_analysis["DRM Pillar"] = template_df["DRM Pillar"].ffill()
    df_analysis["Thematic Area"] = template_df["Thematic Area"]
    
    # Clean pillar names
    df_analysis["DRM Pillar"] = df_analysis["DRM Pillar"].astype(str).str.replace(r'^\d+\.\s*', '', regex=True)
    df_analysis["Thematic Area"] = df_analysis["Thematic Area"].astype(str).str.replace(r'^\d+\.?\d*\.?\s*', '', regex=True)
    
    for idx, row in df_analysis.iterrows():
        # Calculate sum across value columns for this row
        row_sum = sum([float(row[col]) if row[col] != "" and row[col] is not None else 0 for col in value_columns])
        
        if row_sum < 1.0:
            pillar = row["DRM Pillar"]
            subpillar = row["Thematic Area"]
            
            # Determine what to display
            if subpillar and subpillar not in ["nan", "-", ""]:
                below_minimum.append(f"{pillar} - {subpillar}")
            else:
                below_minimum.append(pillar)
    
    # Generate analysis text
    if below_minimum:
        unique_areas = list(dict.fromkeys(below_minimum))  # Remove duplicates while preserving order
        if len(unique_areas) == 1:
            analysis_text = html.Div([
                html.P([
                    html.Strong("⚠️ Areas Below Minimum Standard:"),
                    html.Br(),
                    f"The following area does not meet the minimum standard: "
                ], className="text-warning mb-2"),
                html.Ul([html.Li(area) for area in unique_areas], className="mb-0")
            ], className="alert alert-warning")
        else:
            analysis_text = html.Div([
                html.P([
                    html.Strong("⚠️ Areas Below Minimum Standard:"),
                    html.Br(),
                    f"The following {len(unique_areas)} areas do not meet the minimum standard: "
                ], className="text-warning mb-2"),
                html.Ul([html.Li(area) for area in unique_areas], className="mb-0")
            ], className="alert alert-warning")
    else:
        analysis_text = html.Div([
            html.P([
                html.Strong("✓ All Areas Meet Minimum Standards"),
                html.Br(),
                "Congratulations! All assessed areas meet or exceed the minimum standard."
            ], className="text-success mb-0")
        ], className="alert alert-success")
    
    # Generate figure
    try:
        img_str = generate_figure(df)
        
        figure_html = html.Div([
            html.Img(
                src=f"data:image/png;base64,{img_str}",
                style={"maxWidth": "100%", "height": "auto", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"}
            )
        ])
        
        return {"display": "none"}, {"display": "block"}, img_str, figure_html, analysis_text
    except Exception as e:
        return {"display": "none"}, {"display": "block"}, None, html.Div([
            html.Div(f"Error generating figure: {str(e)}", className="alert alert-danger")
        ]), ""

# Callback for downloading the figure
@app.callback(
    Output("download-image", "data"),
    Input("download-button", "n_clicks"),
    State("figure-store", "data"),
    prevent_initial_call=True
)
def download_figure(n_clicks, img_data):
    """Download the figure as PNG"""
    if img_data is None:
        return None
    
    # Convert base64 back to bytes
    img_bytes = base64.b64decode(img_data)
    
    return dcc.send_bytes(
        img_bytes,
        filename="DRM_Assessment_Result.png"
    )

# Callback to toggle example collapse
@app.callback(
    Output("example-collapse", "is_open"),
    Input("example-button", "n_clicks"),
    State("example-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_example(n_clicks, is_open):
    """Toggle the example data collapse"""
    return not is_open

# Callback to handle Back button - return to Section 1 and clear data
@app.callback(
    [Output("section-1", "style", allow_duplicate=True),
     Output("results-section", "style", allow_duplicate=True),
     Output("pasted-data", "data", allow_duplicate=True),
     Output("paste-input", "value")],
    Input("back-button", "n_clicks"),
    prevent_initial_call=True
)
def go_back(n_clicks):
    """Return to Section 1 and clear pasted data"""
    return {"display": "block"}, {"display": "none"}, None, ""

# Callback to download template file
@app.callback(
    Output("download-template", "data"),
    Input("download-template-button", "n_clicks"),
    prevent_initial_call=True
)
def download_template(n_clicks):
    """Download the DRM System Diagnostic Assessment Template"""
    return dcc.send_file("data/DRM System Diagnostic Assessment - Template.xlsx")


if __name__ == '__main__':
    # Use debug=True for development (auto-reload on code changes)
    # Set to False for production deployment
    is_production = os.environ.get("RENDER", False)
    app.run(debug=not is_production, port=int(os.environ.get("PORT", 8050)))
