"""
Results section layout - charts, analysis, summaries
"""
from dash import dcc, html
import dash_bootstrap_components as dbc


def get_results_section():
    """Return the results section with charts and summaries"""
    return html.Div([
        html.Div([
            html.H3("Assessment Results", className="mb-0", style={"marginTop": "0"}),
            html.Div([
                dbc.Button(
                    [html.I(className="fas fa-download me-2"), "Download Results"],
                    id="download-results-pdf",
                    color="primary",
                    size="sm",
                    className="mt-0 me-2"
                ),
                html.A(
                    [html.I(className="fas fa-file-pdf me-2"), "Download Methodological Note"],
                    href="/assets/documents/DRM Policy Tool - Methodological Note.pdf",
                    download="DRM Policy Tool - Methodological Note.pdf",
                    className="btn btn-primary btn-sm mt-0 me-2"
                ),
                dbc.Button("Back", id="back-button", color="secondary", outline=True, size="sm", className="mt-0")
            ])
        ], className="mb-4 mt-5", style={"display": "flex", "alignItems": "center", "justifyContent": "space-between"}),
        
        # Interpreting the Results section
        html.Div([
            html.P([
                html.Strong("The petal diagram encapsulates the assessment results."),
                " Each petal represents a thematic area of the DRM framework, grouped by thematic area. Below the diagram, results are aggregated by DRM pillar to highlight key drivers and gaps."
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
                html.Strong("The diagnostic should be seen as a starting point for structuring a DRM policy dialogue—not as a final evaluation."),
                " Shorter petals indicate areas where the policy framework is weak and/or not producing the expected outcomes. Depending on a range of factors (e.g., political momentum, internal resources, country prioritization), this policy area may be prioritized for further support. Ultimately, this tool supports policy dialogue—whether to inform the preparation of a Cat DDO operation or to guide Technical Assistance—helping countries shift from reactive disaster response toward a proactive, strategic approach to managing disaster and climate-related risks."
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
    ], id="results-section", style={"display": "none"})
