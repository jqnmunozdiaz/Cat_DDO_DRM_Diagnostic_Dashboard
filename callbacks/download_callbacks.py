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
        Input("questionnaire-inline-link", "n_clicks"),
        prevent_initial_call=True
    )
    def download_template(btn_clicks, link_clicks):
        """Download the DRM System Diagnostic Assessment Template"""
        return dcc.send_file("data/DRM Rapid Screening Tool - Questionnaire.xlsx")

    @app.callback(
        Output("download-methnote", "data"),
        Input("methnote-inline-link", "n_clicks"),
        prevent_initial_call=True
    )
    def download_methnote(n_clicks):
        """Download the Methodological Note"""
        return dcc.send_file("assets/documents/DRM Policy Tool - Methodological Note.pdf")
