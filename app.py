"""
DRM Diagnostic Assessment Tool - Dash Application
Simple one-page dashboard for evaluating country's institutional setting for DRM
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from figure_generator import generate_figure
import base64
from io import BytesIO
import os
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

    # Load the template CSV to get structure
template_df = pd.read_csv("data/DRM_system_assessment_template_filled_example.csv")

# Extract value columns (all columns except DRM Pillar and DRM sub-pillar)
value_columns = [col for col in template_df.columns if col not in ["DRM Pillar", "DRM sub-pillar"]]

# Prepare table data - create editable version with only value columns
def prepare_table_data(empty=False, random_values=False):
    """Prepare table data for the input form"""
    df = template_df.copy()
    if empty:
        # Clear all value columns
        for col in value_columns:
            df[col] = ""
    elif random_values:
        # Fill with random values between 0 and 1
        np.random.seed(42)  # For reproducibility
        for col in value_columns:
            # Generate random values, with some being 0 (empty) for variety
            random_vals = np.random.choice([0, np.random.uniform(0, 1)], size=len(df), p=[0.2, 0.8])
            df[col] = [round(val, 2) if val > 0 else "" for val in random_vals]
    else:
        # Replace "-" with empty string for display
        for col in value_columns:
            df[col] = df[col].astype(str).replace("-", "").replace("nan", "")
    return df

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
            )
        ], width=12)
    ]),
    
    # Main content
    dbc.Row([
        dbc.Col([
            # Section 1: Input Form
            html.Div([
                html.H3("Section 1: Assessment Data", className="mb-4"),
                html.P("Fill in the assessment values for each DRM component with a value between 0 and 1.", className="text-muted"),
                
                # Table container
                html.Div(id="table-container", className="table-responsive"),
                
                # Buttons
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "See Results",
                            id="submit-button",
                            color="primary",
                            size="lg",
                            className="mt-4 me-2"
                        ),
                        dbc.Button(
                            "Reset",
                            id="reset-button",
                            color="secondary",
                            outline=True,
                            size="lg",
                            className="mt-4"
                        )
                    ], width=12)
                ]),
            ], className="section-1 p-4 mb-5 border rounded bg-light"),
            
            # Confirmation Modal for Reset
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Confirm Reset")),
                dbc.ModalBody("Are you sure you want to clear all values? This action cannot be undone."),
                dbc.ModalFooter([
                    dbc.Button("No", id="reset-cancel", className="me-2"),
                    dbc.Button("Yes", id="reset-confirm", color="danger")
                ])
            ], id="reset-modal", centered=True),
            
            # Section 2: Results (hidden initially)
            html.Div([
                html.H3("Section 2: Assessment Results", className="mb-4"),
                
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
    
], fluid=False, style={"maxWidth": "1200px"})

# Callback to generate and update the table
@app.callback(
    Output("table-container", "children"),
    Input("reset-confirm", "n_clicks"),
    prevent_initial_call=False
)
def generate_table(reset_confirm_clicks):
    """Generate the editable table from template"""
    ctx = dash.callback_context
    
    # On initial load, show random values; on reset, show empty table
    if not ctx.triggered or ctx.triggered[0]["prop_id"] == ".":
        df = prepare_table_data(random_values=True)
    else:
        df = prepare_table_data(empty=True)
    
    # Clean the dataframe for display
    df_clean = df.copy()
    
    # Remove leading numbers (e.g., "1. ", "2.1. ") from pillar and sub-pillar names
    df_clean["DRM Pillar"] = df_clean["DRM Pillar"].astype(str).str.replace(r'^\d+\.\s*', '', regex=True)
    df_clean["DRM sub-pillar"] = df_clean["DRM sub-pillar"].astype(str).str.replace(r'^\d+\.?\d*\.?\s*', '', regex=True)
    
    # Forward fill pillar names to replace "nan" with the actual pillar
    df_clean["DRM Pillar"] = df_clean["DRM Pillar"].replace("nan", "").replace("", pd.NA)
    df_clean["DRM Pillar"] = df_clean["DRM Pillar"].ffill()
    
    # Replace "nan" and "-" in sub-pillars with empty string
    df_clean["DRM sub-pillar"] = df_clean["DRM sub-pillar"].replace(["nan", "-"], "")
    
    # Create table
    table = dbc.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("DRM Pillar", style={"width": "20%"}),
                    html.Th("DRM Sub-pillar", style={"width": "25%"}),
                    *[html.Th(col, style={"width": f"{55/len(value_columns):.1f}%"}) for col in value_columns]
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(str(row["DRM Pillar"]) if pd.notna(row["DRM Pillar"]) else "", className="pillar-cell"),
                    html.Td(str(row["DRM sub-pillar"]) if row["DRM sub-pillar"] != "" else "", className="subpillar-cell"),
                    *[
                        html.Td(
                            dbc.Input(
                                type="number",
                                step=0.01,
                                min=0,
                                max=1,
                                value=row[col] if row[col] != "" else None,
                                id={"type": "value-input", "index": f"{idx}-{col}"},
                                className="form-control-sm",
                                placeholder="",
                                debounce=True
                            )
                        ) for col in value_columns
                    ]
                ]) for idx, (_, row) in enumerate(df_clean.iterrows())
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        className="mb-3"
    )
    
    return table

# Callback to handle form submission and generate figure
@app.callback(
    [Output("results-section", "style"),
     Output("figure-store", "data"),
     Output("figure-container", "children")],
    Input("submit-button", "n_clicks"),
    State({"type": "value-input", "index": dash.ALL}, "id"),
    State({"type": "value-input", "index": dash.ALL}, "value"),
    prevent_initial_call=True
)
def update_results(n_clicks, input_ids, input_values):
    """Process form data and generate figure"""
    if not input_ids:
        return {"display": "none"}, None, "No data to process"
    
    # Reconstruct the dataframe from inputs - start with empty table
    df = prepare_table_data(empty=True)
    
    # Create a mapping of row-column to value
    for i, (input_id, value) in enumerate(zip(input_ids, input_values)):
        row_col = input_id["index"]
        # Split by first dash only to get row index
        parts = row_col.split("-", 1)
        if len(parts) == 2:
            row_idx = int(parts[0])
            col_name = parts[1]  # The column name as stored in the ID
            
            # Match with actual column name
            if col_name in value_columns and row_idx < len(df):
                # Validate and convert value
                if value is None or value == "":
                    df.at[row_idx, col_name] = 0
                else:
                    try:
                        num_value = float(value)
                        # Clamp value between 0 and 1
                        num_value = max(0, min(1, num_value))
                        df.at[row_idx, col_name] = num_value
                    except (ValueError, TypeError):
                        df.at[row_idx, col_name] = 0
    
    # Generate figure
    try:
        img_str = generate_figure(df)
        
        figure_html = html.Div([
            html.Img(
                src=f"data:image/png;base64,{img_str}",
                style={"maxWidth": "100%", "height": "auto", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"}
            )
        ])
        
        return {"display": "block"}, img_str, figure_html
    except Exception as e:
        return {"display": "block"}, None, html.Div([
            html.Div(f"Error generating figure: {str(e)}", className="alert alert-danger")
        ])

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

# Callback to open reset confirmation modal
@app.callback(
    Output("reset-modal", "is_open"),
    Input("reset-button", "n_clicks"),
    Input("reset-cancel", "n_clicks"),
    Input("reset-confirm", "n_clicks"),
    State("reset-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_reset_modal(reset_clicks, cancel_clicks, confirm_clicks, is_open):
    """Toggle the reset confirmation modal"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "reset-button":
        return True
    elif button_id in ["reset-cancel", "reset-confirm"]:
        return False
    
    return is_open





# Add validation script
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer></footer>
        {%config%}
        {%scripts%}
        {%renderer%}
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            function validateInputs() {
                document.querySelectorAll('input[type="number"]').forEach(input => {
                    input.addEventListener('change', function() {
                        let val = parseFloat(this.value);
                        if (!isNaN(val)) {
                            if (val < 0) this.value = 0;
                            if (val > 1) this.value = 1;
                        }
                    });
                });
            }
            validateInputs();
            // Re-run after Dash updates
            const observer = new MutationObserver(validateInputs);
            observer.observe(document.body, { childList: true, subtree: true });
        });
        </script>
    </body>
</html>
'''

if __name__ == '__main__':
    # Use debug=True for development (auto-reload on code changes)
    # Set to False for production deployment
    is_production = os.environ.get("RENDER", False)
    app.run(debug=not is_production, port=int(os.environ.get("PORT", 8050)))
