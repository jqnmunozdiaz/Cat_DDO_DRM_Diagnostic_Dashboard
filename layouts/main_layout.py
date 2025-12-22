"""
Main layout - combines all layout components
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

from layouts.header import get_header
from layouts.input_section import get_input_section
from layouts.results_section import get_results_section


def get_layout():
    """Return the complete app layout"""
    return dbc.Container([
        # Header with logos and title
        *get_header(),
        
        # Main content
        dbc.Row([
            dbc.Col([
                # Input section
                get_input_section(),
                
                # Results section (hidden initially)
                get_results_section(),
                
            ], width=12, lg=10)
        ], justify="center"),
        
        # Hidden stores
        dcc.Store(id="figure-store"),
        dcc.Store(id="pasted-data"),
        
    ], fluid=False, style={"maxWidth": "1200px"})


# Export the layout
layout = get_layout()
