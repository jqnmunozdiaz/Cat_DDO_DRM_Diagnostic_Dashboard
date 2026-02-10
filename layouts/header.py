"""
Header layout component - logos and title
"""
from dash import html
import dash_bootstrap_components as dbc

def get_header():
    """Return the header section with logos and title"""
    return [
        # Header with logos
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src="/assets/images/wb-full-logo.png", height="60px", className="me-3"),
                    html.Img(src="/assets/images/gfdrr-logo.png", height="60px")
                ], style={"display": "flex", "alignItems": "center", "justifyContent": "center", "marginBottom": "20px", "gap": "20px"})
            ], width=12)
        ]),
        
        # Title
        dbc.Row([
            dbc.Col([
                html.H1("Disaster Risk Management Policy Diagnostic Tool", className="mb-2 text-center"),
                html.P(
                    "Evaluate a country's policy and institutional setting for Disaster Risk Management across six critical pillars",
                    className="text-center text-muted mb-4 lead"
                ),
                dbc.Alert(
                    [html.B("Prototype"), ": this will be updated following test cases. Your feedback is welcomed."],
                    color="info",
                    className="mb-4 text-center"
                )
            ], width=12)
        ]),
    ]
