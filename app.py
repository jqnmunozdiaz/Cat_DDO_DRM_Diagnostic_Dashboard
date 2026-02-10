"""
DRM Diagnostic Assessment Tool - Dash Application
Simple one-page dashboard for evaluating country's institutional setting for DRM
"""
import os
import dash
import dash_bootstrap_components as dbc

from layouts.main_layout import layout
from callbacks import register_callbacks

# Initialize app
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    title="DRM Policy Diagnostic Tool"
)
server = app.server

# Set layout
app.layout = layout

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    # Use debug=True for development (auto-reload on code changes)
    # Set to False for production deployment
    is_production = os.environ.get("RENDER", False)
    app.run(debug=not is_production, port=int(os.environ.get("PORT", 8050)))
