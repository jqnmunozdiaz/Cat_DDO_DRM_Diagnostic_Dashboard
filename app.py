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

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Load the template CSV to get structure
template_df = pd.read_csv("data/DRM_system_assessment_template_filled_example.csv")

# Extract value columns (all columns except DRM Pillar and DRM sub-pillar)
value_columns = [col for col in template_df.columns if col not in ["DRM Pillar", "DRM sub-pillar"]]

# Prepare table data - create editable version with only value columns
def prepare_table_data():
    """Prepare table data for the input form"""
    df = template_df.copy()
    # Replace "-" with empty string for display
    for col in value_columns:
        df[col] = df[col].astype(str).replace("-", "").replace("nan", "")
    return df

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("DRM Diagnostic Assessment Tool", className="mb-2 mt-5 text-center"),
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
                html.P("Fill in the assessment values for each DRM component. Leave blank or enter 0 for not applicable (-).", className="text-muted"),
                
                # Table container
                html.Div(id="table-container", className="table-responsive"),
                
                # See Results button
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "See Results",
                            id="submit-button",
                            color="primary",
                            size="lg",
                            className="mt-4 w-100"
                        )
                    ], width=12)
                ]),
            ], className="section-1 p-4 mb-5 border rounded bg-light"),
            
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
    Input("submit-button", "n_clicks"),
    prevent_initial_call=True
)
def generate_table(n_clicks):
    """Generate the editable table from template"""
    df = prepare_table_data()
    
    # Create table
    table = dbc.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("DRM Pillar", width="20%"),
                    html.Th("DRM Sub-pillar", width="25%"),
                    *[html.Th(col, width=f"{55/len(value_columns):.1f}%") for col in value_columns]
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(str(row["DRM Pillar"]), className="pillar-cell"),
                    html.Td(str(row["DRM sub-pillar"]), className="subpillar-cell"),
                    *[
                        html.Td(
                            dbc.Input(
                                type="number",
                                step=0.01,
                                min=0,
                                max=1,
                                value=row[col] if row[col] != "" else None,
                                id={"type": "value-input", "index": f"{idx}-{col}"},
                                className="form-control-sm"
                            )
                        ) for col in value_columns
                    ]
                ]) for idx, (_, row) in enumerate(df.iterrows())
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
    
    # Reconstruct the dataframe from inputs
    df = prepare_table_data()
    
    # Create a mapping of row-column to value
    for i, (input_id, value) in enumerate(zip(input_ids, input_values)):
        row_col = input_id["index"]
        parts = row_col.rsplit("-", 1)
        if len(parts) == 2:
            row_idx = int(parts[0])
            col_name = "-".join(parts[1:])  # In case column has "-" in name
            
            # Find the actual column name
            for col in value_columns:
                if col.replace(" ", "-") in row_col or row_col.endswith(col.replace(" ", "-")):
                    if row_idx < len(df):
                        df.at[row_idx, col] = value if value is not None else 0
                    break
    
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

# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px 0;
            }
            .container-fluid, .container {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                margin-top: 20px;
                margin-bottom: 40px;
            }
            h1 {
                color: #667eea;
                font-weight: 700;
            }
            h3 {
                color: #764ba2;
                font-weight: 600;
                margin-top: 30px;
            }
            .section-1, .section-2 {
                background-color: #f8f9fa;
                border-color: #dee2e6 !important;
            }
            .table {
                margin-bottom: 0;
            }
            .table th {
                background-color: #667eea;
                color: white;
                font-weight: 600;
                border: none;
                text-align: center;
            }
            .table td {
                vertical-align: middle;
                border-color: #dee2e6;
            }
            .pillar-cell, .subpillar-cell {
                font-weight: 500;
                background-color: #f0f0f0;
                color: #333;
            }
            .form-control-sm {
                border: 1px solid #ccc;
                padding: 6px 8px;
                font-size: 0.9rem;
            }
            .form-control-sm:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
            }
            .btn {
                border-radius: 6px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-primary {
                background-color: #667eea;
                border-color: #667eea;
            }
            .btn-primary:hover {
                background-color: #5568d3;
                border-color: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            .btn-success {
                border-color: #28a745;
                color: #28a745;
            }
            .btn-success:hover {
                background-color: #28a745;
                color: white;
            }
            .text-muted {
                color: #6c757d !important;
                font-size: 0.95rem;
            }
            .lead {
                font-size: 1.1rem;
                font-weight: 500;
            }
            .table-responsive {
                border-radius: 6px;
                overflow: hidden;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer></footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=False, port=int(os.environ.get("PORT", 8050)))
