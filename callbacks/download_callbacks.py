"""
Download callbacks - file download functionality
"""
import base64
from dash import dcc, Input, Output, State
import plotly.graph_objects as go


def _create_image_download(fig_data, filename, width=1000, height=1000, scale=2):
    """
    Shared helper to convert a Plotly figure to a PNG download dict.
    Returns None if fig_data is invalid.
    """
    if fig_data is None:
        return None
    
    try:
        fig = go.Figure(fig_data)
        img_bytes = fig.to_image(format="png", width=width, height=height, scale=scale)
        return {
            "content": base64.b64encode(img_bytes).decode(),
            "filename": filename,
            "base64": True
        }
    except Exception as e:
        print(f"Error generating image download for {filename}: {str(e)}")
        return None


def register_download_callbacks(app):
    """Register download-related callbacks"""
    
    @app.callback(
        Output("download-image", "data"),
        Input("download-button", "n_clicks"),
        State("petal-chart", "figure"),
        prevent_initial_call=True
    )
    def download_figure(n_clicks, fig_data):
        """Download the petal chart as PNG"""
        if not n_clicks:
            return None
        return _create_image_download(fig_data, "DRM_Assessment_Result.png")

    @app.callback(
        Output("download-pillar-image", "data"),
        Input("download-pillar-button", "n_clicks"),
        State("pillar-progress-bars", "figure"),
        prevent_initial_call=True
    )
    def download_pillar_figure(n_clicks, fig_data):
        """Download the pillar progress bars as PNG"""
        if not n_clicks:
            return None
        # Calculate height based on number of bars
        num_bars = len(fig_data['data'][0]['y']) if fig_data and fig_data.get('data') and len(fig_data['data']) > 0 else 6
        height = max(400, num_bars * 60)
        return _create_image_download(fig_data, "DRM_Pillar_Progress.png", height=height)

    @app.callback(
        Output("download-template", "data"),
        Input("download-template-button", "n_clicks"),
        prevent_initial_call=True
    )
    def download_template(n_clicks):
        """Download the DRM System Diagnostic Assessment Template"""
        return dcc.send_file("data/DRM System Diagnostic Assessment - Template.xlsx")
