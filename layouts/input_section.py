"""
Input section layout - introduction, guidelines, country dropdown, paste area
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from config.constants import COUNTRIES, EXAMPLE_DATA

def get_input_section():
    """Return the input section with introduction, guidelines, and form"""
    return html.Div([
        # Introduction
        html.Div([
            html.H3("Introduction", className="mb-3"),
            html.P([
                html.Strong("The objective of this web tool is to allow practitioners to conduct an assessment of the maturity of a country's Disaster Risk Management (DRM) system and identify the main policy gaps that may be constraining resilience-building efforts. "), 
                "Recognizing that a comprehensive DRM policy diagnostic requires a system-wide perspective, this tool is organized around the World Bank’s DRM framework, which outlines six key DRM policy dimensions. The reader is referred to the accompanying Methodological Note for a thorough description of the DRM framework and this tool."
            ], className="text-muted"),
            html.Div([
                html.Img(src="/assets/images/Policy_Framework.png", 
                         style={"maxWidth": "100%", "height": "auto", "display": "block", "margin": "0 auto", "marginBottom": "20px"})
            ], className="text-center mt-3"),
        ], className="mb-4"),
        
        # Guidelines section
        html.Div([
            html.P([
                html.Strong("This is a high-level assessment designed to be objective and quick."), 
                " The tool assesses each DRM pillar using a set of closed Yes/No questions presented in an offline questionnaire. Users should review official documentation (legal, regulatory, institutional, and budgetary) and consult with colleagues and national authorities to provide an informed answer. This is particularly relevant for cross-cutting questions, where inputs from colleagues from sectors such as Water, Transport, Education, Health, and Agriculture may help in gathering information. Once all questions are completed, the web tool will generate key metrics and visual outputs."
            ], className="text-muted")
        ], className="mb-4"),
                    
        # Input Form
        html.Div([
            # Country selection dropdown
            dbc.Row([
                dbc.Col([
                    html.Label("1. Select the country:", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id="country-dropdown",
                        options=[{"label": country, "value": country} for country in COUNTRIES],
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
                        className="mb-3 me-2",
                        n_clicks=0
                    ),
                    dcc.Download(id="download-template"),
                    html.A(
                        [html.I(className="fas fa-file-pdf me-2"), "Download Methodological Note"],
                        href="/assets/documents/DRM Policy Tool - Methodological Note.pdf",
                        download="DRM Policy Tool - Methodological Note.pdf",
                        className="btn btn-primary mb-3"
                    ),
                ], width=12)
            ]),
            
            # Paste area
            html.Div([
                html.Label("2. Copy and paste the data from cell B10 of the spreadsheet after completing the diagnostic:", className="form-label fw-bold"),
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
                            "You can copy the following text of an example diagnostic and paste it in the box above to see how the tool works.",
                            className="form-text text-muted mb-2"
                        ),
                        dbc.Card(dbc.CardBody([
                            html.Pre(
                                EXAMPLE_DATA,
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
    ])
