"""
Download callbacks - file download functionality
"""
from dash import dcc, Input, Output

def register_download_callbacks(app):
    """
    Register download-related callbacks.
    """
    @app.callback(
        Output("download-template", "data"),
        Input("download-template-button", "n_clicks"),
        prevent_initial_call=True
    )
    def download_template(n_clicks):
        """Download the DRM System Diagnostic Assessment Template"""
        return dcc.send_file("data/DRM System Diagnostic Assessment - Template.xlsx")
