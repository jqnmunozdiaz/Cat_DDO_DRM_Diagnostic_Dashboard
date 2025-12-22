"""
UI callbacks - toggle, navigation, and UI interactions
"""
from dash import Input, Output, State


def register_ui_callbacks(app):
    """Register UI-related callbacks"""
    
    @app.callback(
        Output("example-collapse", "is_open"),
        Input("example-button", "n_clicks"),
        State("example-collapse", "is_open"),
        prevent_initial_call=True
    )
    def toggle_example(n_clicks, is_open):
        """Toggle the example data collapse"""
        return not is_open

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
