"""
DRM Diagnostic Assessment Tool - Dash Application
Simple one-page dashboard for evaluating country's institutional setting for DRM
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from scripts.petal_chart_figure_generator import generate_figure
from scripts.pillar_chart import generate_pillar_chart
from utils.data_parser import parse_pasted_data
from config.question_config import THEMATIC_AREA_QUESTIONS, parse_question_range
import plotly.graph_objects as go
import base64
import os
import json
from pathlib import Path

# Initialize the Dash app
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ], 
    suppress_callback_exceptions=True
)
server = app.server

# Helper functions
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
            html.H1("A Disaster Risk Management Policy Diagnostic Tool", className="mb-2 text-center"),
            html.P(
                "Evaluate your country's policy and institutional setting for Disaster Risk Management across six critical pillars",
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
                html.H3("Introduction", className="mb-3"),

                html.P([
                    html.Strong("A sound Disaster Risk Management (DRM) policy assessment requires a system-wide perspective. "), "Unlike traditional sectors, DRM cuts across infrastructure sectors, such as energy, water, transport, urban development, as well as socioenvironmental sectors, such as education, health, social protection and environmental management. Disaster risk also affects economic growth, fiscal stability and jobs. In short, disaster risk is a development challenge arising from the interaction of hazard, exposure, and vulnerability. While managing the immediate impacts of disasters is vital, building disaster resilience therefor requires a more comprehensive, multisectoral policy approach."
                ], className="text-muted"),
                
                html.P([
                    html.Strong("Recognizing this, the World Bank DRM framework provides a structured approach to evaluate a country's policy and institutional setup for DRM. "), "Drawing on practical country experiences and global good practices, this framework was first proposed in 'The Sendai Report' (Ghesquiere et al. 2012) and is aligned with the Sendai Framework for Disaster Risk Reduction. It is organized around six essential components of DRM encompassing not only legal and institutional DRM frameworks, but also key policy dimensions related to risk information, risk reduction at the sectoral and territorial level, emergency preparedness and response, financial protection and resilient recovery."
                ], className="text-muted"),
                
                html.Div([
                    html.Img(src="/assets/images/Policy_Framework.png", 
                             style={"maxWidth": "100%", "height": "auto", "display": "block", "margin": "0 auto", "marginBottom": "20px"})
                ], className="text-center mt-3"),
                
                html.P([
                    html.Strong("Building upon this framework, the proposed diagnostic tool enables task teams to conduct a standardized assessment of the maturity of a country's DRM system. The goal is to identify the main policy gaps that may be constraining resilience-building efforts across each DRM pillar.")
                ], className="text-muted"),
                
            ], className="mb-4"),
            
            # Guidelines section
            html.Div([
                html.H3("Guidelines for Using the Tool", className="mb-3"),
                                
                html.P([
                    html.Strong("The tool assesses each DRM pillar using a set of closed questions presented in an Excel-based questionnaire."), 
                    " Task teams can download the file for offline completion. To ensure objectivity and speed, teams are asked to provide a \"Yes\" or \"No\" answer. This answer must be based on official documents that justify the existence of a series of legal, regulatory, institutional, and budgetary conditions that are considered fundamental for managing disaster risk."
                ], className="text-muted"),
                
                html.P([
                    "This is a high-level assessment designed to be completed quickly. If information for a question is unavailable, teams are encouraged to consult other Global Practice (GP) colleagues or national counterparts. This is particularly relevant under Pillar 3, where inputs from colleagues in the Water, Transport, Education, Health, and Agriculture GP can greatly help in gathering information."
                ], className="text-muted"),
                
                html.P([
                    "Once all questions are completed, copy/paste the content of the Excel below. The system will automatically generate key metrics and visual outputs."
                ], className="text-muted"),
                
            ], className="mb-4"),
            
            # Section 1: Input Form
            html.Div([
                # Country selection dropdown
                dbc.Row([
                    dbc.Col([
                        html.Label("Select Country:", className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id="country-dropdown",
                            options=[
                                {"label": country, "value": country} for country in [
                                    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda",
                                    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
                                    "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
                                    "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria",
                                    "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada",
                                    "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros",
                                    "Congo (Republic of)", "Congo (DRC)", "Costa Rica", "Croatia", "Cuba",
                                    "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic",
                                    "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia",
                                    "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia",
                                    "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
                                    "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran",
                                    "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan",
                                    "Kenya", "Kiribati", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon",
                                    "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
                                    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
                                    "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia",
                                    "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal",
                                    "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea",
                                    "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama",
                                    "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar",
                                    "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia",
                                    "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe",
                                    "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore",
                                    "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea",
                                    "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland",
                                    "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo",
                                    "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
                                    "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States",
                                    "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam",
                                    "Yemen", "Zambia", "Zimbabwe"
                                ]
                            ],
                            value="Angola",
                            placeholder="Select a country...",
                            clearable=False,
                            className="mb-3"
                        )
                    ], width=12)
                ], className="mb-3"),
                
                # Download template button
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-download me-2"), "Download Diagnostic Questionnaire"],
                            id="download-template-button",
                            color="primary",
                            className="mb-3",
                            n_clicks=0
                        ),
                        dcc.Download(id="download-template")
                    ], width=12)
                ]),
                

                # Paste area to bulk-populate the table
                html.Div([
                    html.Label("Please paste the data from cell B10 of your spreadsheet after completing the diagnostic:", className="form-label fw-semibold"),
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
                                "Enter the text following the required format. You can copy and paste the following example to proceed.",
                                className="form-text text-muted mb-2"
                            ),
                            dbc.Card(dbc.CardBody([
                                html.Pre(
                                    "Q1,Yes,1;Q2,No,1;Q3,No,0.5;Q4,Yes,0.5;Q5,No,1;Q6,Yes,1;Q7,No,1;Q8,Yes,0.5;Q9,Yes,0.5;Q10,Yes,1;Q11,No,1;Q12,No,0.5;Q13,Yes,0.5;Q14,Yes,1;Q15,No,1;Q16,Yes,1;Q17,Yes,1;Q18,No,0.25;Q19,No,0.25;Q20,Yes,0.25;Q21,Yes,0.25;Q22,No,1;Q23,Yes,1;Q24,No,1;Q25,No,1;Q26,No,0.5;Q27,No,0.5;Q28,Yes,1;Q29,Yes,1;Q30,Yes,1;Q31,Yes,1;Q32,No,0.5;Q33,No,0.5;Q34,Yes,1;Q35,Yes,1;Q36,Yes,1;Q37,Yes,1;Q38,Yes,1;Q39,Yes,1;Q40,Yes,0.5;Q41,Yes,0.5;Q42,Yes,1;Q43,Yes,1;Q44,Yes,1;Q45,Yes,1;Q46,No,1;Q47,Yes,1",
                                    style={"whiteSpace": "pre-wrap", "fontFamily": "monospace", "fontSize": "0.85rem"}
                                )
                            ]))
                        ],
                        id="example-collapse",
                        is_open=False,
                        className="mt-2"
                    )
                ], className="mb-4")
            ], id="section-1"),

            # Section 2: Results (hidden initially)
            html.Div([
                # Title with Back button on the right
                html.Div([
                    html.H3("Assessment Results", className="mb-3 mt-0"),
                    dbc.Button("Back", id="back-button", color="secondary", outline=True, size="sm", className="mt-0")
                ], className="mb-4", style={"display": "flex", "alignItems": "flex-start", "justifyContent": "space-between"}),
                
                # Interpreting the Results section
                html.Div([
                    
                    html.P([
                        "The petal diagram encapsulates the assessment results. Each petal represents a thematic area of the DRM framework, grouped by thematic area. Below the diagram, results are aggregated by DRM pillar to highlight key drivers and gaps."
                    ], className="text-muted"),
                    
                    html.Ul([
                        html.Li([html.Strong("Petal length"), " reflects progress in that thematic area: the longer the size of the petal, the more advanced the country is."]),
                        html.Li([html.Strong("When a petal extends beyond the red circle"), ", minimum policy requirements for that area are considered in place."]),
                        html.Li([html.Strong("Countries with mature DRM systems"), " typically have most petals exceeding the red circle, with some approaching the frontier (i.e., exhibiting a level of advances close to the global benchmark frontier)."]),
                    ], className="text-muted"),
                    
                ], className="mb-4"),
                
                # Closing interpretation text
                html.Div([
                    html.P([
                        "The diagnostic should be seen as a starting point for structuring a DRM policy dialogue—not as a final evaluation. Shorter petals indicate areas where the policy framework is weak and/or not producing the expected outcomes. Depending on a range of factors (e.g., political momentum, internal resources, country prioritization), this policy area may be prioritized for further support. Ultimately, this tool supports policy dialogue—whether to inform the preparation of a Cat DDO operation or to guide Technical Assistance—helping countries shift from reactive disaster response toward a proactive, strategic approach to managing disaster and climate-related risks."
                    ], className="text-muted"),
                    
                    html.P([
                        "While the evaluation reflects lessons learned and good practices that can serve as a foundation for a robust DRM policy framework, it should not be interpreted as prescriptive guidance. Disaster risk is highly context-specific, and this diagnostic represents only an initial step toward developing an appropriate and effective DRM policy program. Task teams are encouraged to consult the report ", 
                        html.A(html.Em("Driving Resilience Through Policy Reforms"), href="https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099101125110542181"), 
                        " for further guidance on how to structure a context-relevant DRM policy program."
                    ], className="text-muted"),
                    
                ], className="mb-4"),

                # Figure container
                html.Div(
                    id="figure-container",
                    className="text-center mb-4"
                ),
                
                # Progress bars by pillar
                html.Div([
                    html.Div([
                        html.H5("Results by DRM Pillar", className="mb-3 mt-0"),
                        dbc.Button(
                            "Download Figure",
                            id="download-pillar-button",
                            color="success",
                            outline=True,
                            size="sm",
                            className="mt-0"
                        )
                    ], style={"display": "flex", "alignItems": "flex-start", "justifyContent": "space-between"}, className="mb-3"),
                    dcc.Graph(id="pillar-progress-bars", config={'displayModeBar': False},
                             style={"maxWidth": "100%", "height": "auto", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"}),
                    dcc.Download(id="download-pillar-image")
                ], className="mb-4"),
                
                # Analysis text
                html.Div(id="analysis-text", className="mb-4"),
                
                # Summary by Thematic Area section
                html.Div([
                    html.H4("Summary by Thematic Area", className="mb-3"),
                    html.Div([
                        html.P([
                            html.I(className="fas fa-info-circle me-2"),
                            "This text was generated automatically by a Large Language Model (LLM). Users should verify the content and cross-reference with official documentation."
                        ], className="text-muted fst-italic small mb-3", style={"backgroundColor": "#fff3cd", "padding": "10px", "borderRadius": "5px", "border": "1px solid #ffc107"})
                    ]),
                    
                    # Dynamic summaries container
                    html.Div(id="thematic-summaries-container")
                    
                ], className="mb-4")
            ], id="results-section", className="section-2 p-4 border rounded", style={"display": "none", "backgroundColor": "#f8f9fa"}),
            
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
    result = parse_pasted_data(raw_text or "")
    if result[0] is None:
        return dash.no_update, html.Div(result[-1], className="alert alert-danger")
    df_parsed, question_data, status = result
    # Serialize parsed dataframe (pillar, thematic, score) and question answers
    serialized = {
        'df': df_parsed.to_dict('records'),
        'questions': question_data
    }
    return serialized, html.Div(status, className="alert alert-success")

# Callback to generate results on paste or See Results button
@app.callback(
    [Output("section-1", "style"),
     Output("results-section", "style"),
     Output("figure-store", "data"),
     Output("figure-container", "children"),
     Output("analysis-text", "children"),
     Output("pillar-progress-bars", "figure"),
     Output("thematic-summaries-container", "children")],
    Input("paste-apply", "n_clicks"),
    Input("pasted-data", "data"),
    State("country-dropdown", "value"),
    prevent_initial_call=True
)
def update_results(n_clicks, pasted_data, country):
    """Process pasted data and generate figure"""
    if not pasted_data:
        raise dash.exceptions.PreventUpdate
    
    # Build dataframe from pasted data
    df = pd.DataFrame(pasted_data['df'])
    question_data = pasted_data['questions']
    
    # Analyze results - find areas below minimum standard (1.0)
    below_minimum = []
    
    for idx, row in df.iterrows():
        if row["Score"] < 0.25:
            thematic = row["Thematic Area"]
            # Remove leading numbers from thematic area name
            clean_thematic = thematic.split('. ', 1)[1] if '. ' in thematic else thematic
            below_minimum.append(clean_thematic)
    
    # Generate analysis text
    if below_minimum:
        if len(below_minimum) == 1:
            analysis_text = html.Div([
                html.P([
                    html.Strong("⚠️ Areas Below Minimum Standard:"),
                    html.Br(),
                    f"The following area does not meet the minimum standard: "
                ], className="text-warning mb-2"),
                html.Ul([html.Li(area) for area in below_minimum], className="mb-0")
            ], className="alert alert-warning")
        else:
            analysis_text = html.Div([
                html.P([
                    html.Strong(f"⚠️ The following {len(below_minimum)} areas do not meet the minimum standard:"),
                ], className="text-warning mb-2"),
                html.Ul([html.Li(area) for area in below_minimum], className="mb-0")
            ], className="alert alert-warning")
    else:
        analysis_text = html.Div([
            html.P([
                html.Strong("✓ Congratulations! All assessed areas meet or exceed the minimum standard."),
            ], className="text-success mb-0")
        ], className="alert alert-success")
    
    # Generate pillar progress chart
    progress_fig = generate_pillar_chart(df)
    
    # Generate thematic area summaries
    thematic_summaries = []
    for area_config in THEMATIC_AREA_QUESTIONS:
        thematic_name = area_config["thematic"]
        # Generate indicator for this thematic area
        indicator = generate_answer_indicator(question_data, thematic_name)
        # Load summary from JSON
        summary_text = load_thematic_summary(thematic_name, indicator)
        
        # Replace {country} placeholder with actual country name
        if country:
            summary_text = summary_text.replace("{country}", country)
        
        # Create summary HTML
        # Remove leading numbers from thematic area name
        clean_thematic = thematic_name.split('. ', 1)[1] if '. ' in thematic_name else thematic_name
        
        # Check if this area is below minimum standard
        is_below_minimum = clean_thematic in below_minimum
        title_style = {"color": "red"} if is_below_minimum else {}
        
        thematic_summaries.append(
            html.Div([
            html.P(html.Strong(clean_thematic, style=title_style), className="mb-2"),
            html.P(summary_text, className="text-muted")
            ], className="mb-3")
        )
    
    # Generate circular figure
    try:
        img_str = generate_figure(df)
        
        figure_html = html.Div([
            html.Div([
                html.H5("Results by Thematic Area", className="mb-3 mt-0"),
                dbc.Button(
                    "Download Figure",
                    id="download-button",
                    color="success",
                    outline=True,
                    size="sm",
                    className="mt-0"
                )
            ], style={"display": "flex", "alignItems": "flex-start", "justifyContent": "space-between"}, className="mb-3"),
            html.Img(
                src=f"data:image/png;base64,{img_str}",
                style={"maxWidth": "100%", "height": "auto", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"}
            ),
            dcc.Download(id="download-image")
        ])
        
        return {"display": "none"}, {"display": "block"}, img_str, figure_html, analysis_text, progress_fig, thematic_summaries
    except Exception as e:
        return {"display": "none"}, {"display": "block"}, None, html.Div([
            html.Div(f"Error generating figure: {str(e)}", className="alert alert-danger")
        ]), "", go.Figure(), []
        
    

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

# Callback for downloading the pillar progress bars figure
@app.callback(
    Output("download-pillar-image", "data"),
    Input("download-pillar-button", "n_clicks"),
    State("pillar-progress-bars", "figure"),
    prevent_initial_call=True
)
def download_pillar_figure(n_clicks, fig_data):
    """Download the pillar progress bars as PNG"""
    if fig_data is None or not n_clicks:
        return None
    
    try:
        # Recreate the figure from the stored data
        fig = go.Figure(fig_data)
        
        # Calculate height based on number of bars
        num_bars = len(fig_data['data'][0]['y']) if fig_data.get('data') and len(fig_data['data']) > 0 else 6
        height = max(400, num_bars * 60)
        
        # Convert to image bytes
        img_bytes = fig.to_image(format="png", width=1000, height=height)
        
        return dcc.send_bytes(
            img_bytes,
            filename="DRM_Pillar_Progress.png"
        )
    except Exception as e:
        print(f"Error downloading pillar figure: {str(e)}")
        return None

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
