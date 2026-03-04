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
            html.P([
                html.Strong("This web tool allows practitioners to conduct an assessment of a country's Disaster Risk Management (DRM) policy framework.  "), 
                "Recognizing that a comprehensive policy diagnostic requires a system-wide perspective, the tool is organized around the World Bank’s DRM framework, which outlines six key DRM policy dimensions. The reader is referred to the accompanying ",
                html.Span("Methodological Note", id="methnote-inline-link", n_clicks=0, style={"cursor": "pointer", "textDecoration": "underline", "color": "#0d6efd"}),
                " for a thorough description of the DRM framework and this tool."
            ], className="text-muted"),

            html.Div([
                html.H3("World Bank DRM Policy Framework", className="mb-3", style={"fontSize": "1.4rem"}),
                html.Img(src="/assets/images/Policy_Framework.png", 
                         style={"maxWidth": "100%", "height": "auto", "display": "block", "margin": "0 auto", "marginBottom": "20px"})
            ], className="text-center mt-3"),
        ], className="mb-4"),
        
        # Guidelines section
        html.Div([
            html.P([
                html.Strong("This is a high-level assessment designed to be objective and quick. "), 
                "Each DRM thematic area is evaluated using a set of closed Yes/No questions contained in an offline ",
                html.Span("Questionnaire", id="questionnaire-inline-link", n_clicks=0, style={"cursor": "pointer", "textDecoration": "underline", "color": "#0d6efd"}),
                ". Within each thematic area, questions follow the results chain logic used in Development Policy Financing (DPF) operations, progressing from policy and institutional inputs, through reform implementation, to outputs and outcomes that contribute to strengthened disaster resilience. Users should review official documentation (legal, regulatory, institutional, and budgetary) and report sources in the “support documentation” column, including where possible, electronic links to enhance transparency and robustness. While some questions can be addressed through desk review, others may require consultations with colleagues and national authorities. This is particularly relevant for cross-cutting questions, where inputs from colleagues from sectors such as Water, Transport, Education, Health, and Agriculture may help in gathering information."
            ], className="text-muted"),
            html.P([
                html.Strong("This tool is intended to support in-country DRM policy dialogue, operational engagements, and technical assistance design. "), 
                "It provides a diagnostic of the DRM framework that should be viewed as an entry point for structured policy dialogue rather than a definitive or exhaustive assessment. In practice, the insights that users will gain by completing the questionnaire are as important as the final results. Users are therefore encouraged to record qualitative observations in the “notes/comments” column. This space may be used to clarify responses (for example, to note weaknesses despite a “Yes” response, or strengths despite a “No” response), or to flag a potential policy reform identified during the diagnostic. If users are uncertain about a response, they may select the “Unknown” option and provide additional context in the comments, including which national counterparts or colleagues could help clarify the issue. This information can facilitate the identification of key stakeholders to be engaged during initial phases of the policy dialogue."
            ], className="text-muted"),
            html.P([
                html.Strong("Once all questions are completed, the web tool will automatically generate key metrics and visual outputs across each DRM thematic area. "), 
                "Together these outputs help identify relative strengths and weaknesses within the DRM system and support the prioritization of reforms that may be considered under DPF operations."
            ], className="text-muted"),

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
                    dcc.Download(id="download-methnote"),
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
