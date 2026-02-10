"""
Data callbacks - parsing and processing user input
"""
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

from utils.data_parser import parse_pasted_data
from utils.thematic_helpers import generate_answer_indicator, load_thematic_summary
from scripts.petal_chart_figure_generator import generate_figure
from scripts.pillar_chart import generate_pillar_chart
from config.question_config import THEMATIC_AREA_QUESTIONS


def register_data_callbacks(app):
    """Register data-related callbacks"""
    
    @app.callback(
        Output("pasted-data", "data"),
        Output("paste-feedback", "children"),
        Input("paste-apply", "n_clicks"),
        State("paste-input", "value"),
        prevent_initial_call=True
    )
    def handle_paste(n_clicks, raw_text):
        if not n_clicks:
            raise dash.exceptions.PreventUpdate
        result = parse_pasted_data(raw_text or "")
        if result[0] is None:
            return dash.no_update, html.Div(result[-1], className="alert alert-danger")
        df_parsed, question_data, status = result
        # Serialize parsed dataframe (pillar, thematic, score) and question answers
        serialized = {
            'df': df_parsed.to_dict('records'),
            'questions': question_data
        }
        return serialized, html.Div(status, className="alert alert-success")

    @app.callback(
        [Output("section-1", "style"),
         Output("results-section", "style"),
         Output("figure-store", "data"),
         Output("figure-container", "children"),
         Output("analysis-text", "children"),
         Output("pillar-progress-bars", "figure"),
         Output("thematic-summaries-container", "children")],
        Input("paste-apply", "n_clicks"),
        Input("pasted-data", "data"),
        State("country-dropdown", "value"),
        prevent_initial_call=True
    )
    def update_results(n_clicks, pasted_data, country):
        """Process pasted data and generate figure"""
        if not pasted_data:
            raise dash.exceptions.PreventUpdate
        
        # Build dataframe from pasted data
        df = pd.DataFrame(pasted_data['df'])
        question_data = pasted_data['questions']
        
        # Analyze results - find areas below minimum standard (1.0)
        below_minimum = []
        
        for idx, row in df.iterrows():
            if row["Score"] < 0.25:
                thematic = row["Thematic Area"]
                # Remove leading numbers from thematic area name
                clean_thematic = thematic.split('. ', 1)[1] if '. ' in thematic else thematic
                below_minimum.append(clean_thematic)
        
        # Generate analysis text
        if below_minimum:
            if len(below_minimum) == 1:
                analysis_text = html.Div([
                    html.P([
                        html.Strong("⚠️ Areas Below Minimum Standard:"),
                        html.Br(),
                        f"The following area does not meet the minimum standard: "
                    ], className="text-warning mb-2"),
                    html.Ul([html.Li(area) for area in below_minimum], className="mb-0")
                ], className="alert alert-warning")
            else:
                analysis_text = html.Div([
                    html.P([
                        html.Strong(f"⚠️ The following {len(below_minimum)} areas do not meet the minimum standard:"),
                    ], className="text-warning mb-2"),
                    html.Ul([html.Li(area) for area in below_minimum], className="mb-0")
                ], className="alert alert-warning")
        else:
            analysis_text = html.Div([
                html.P([
                    html.Strong("✓ Congratulations! All assessed areas meet or exceed the minimum standard."),
                ], className="text-success mb-0")
            ], className="alert alert-success")
        
        # Generate pillar progress chart
        progress_fig = generate_pillar_chart(df)
        
        # Generate thematic area summaries
        thematic_summaries = []
        for area_config in THEMATIC_AREA_QUESTIONS:
            thematic_name = area_config["thematic"]
            # Generate indicator for this thematic area
            indicator = generate_answer_indicator(question_data, thematic_name)
            # Load summary from JSON
            summary_text = load_thematic_summary(thematic_name, indicator)
            
            # Replace {country} placeholder with actual country name
            if country:
                summary_text = summary_text.replace("{country}", country)
            
            # Create summary HTML
            # Remove leading numbers from thematic area name
            clean_thematic = thematic_name.split('. ', 1)[1] if '. ' in thematic_name else thematic_name
            
            # Check if this area is below minimum standard
            is_below_minimum = clean_thematic in below_minimum
            title_style = {"color": "red"} if is_below_minimum else {}
            
            thematic_summaries.append(
                html.Div([
                html.P(html.Strong(clean_thematic, style=title_style), className="mb-2"),
                html.P(summary_text, className="text-muted")
                ], className="mb-3")
            )
        
        # Generate circular figure (Plotly)
        try:
            petal_fig = generate_figure(df)
            
            figure_html = html.Div([
                html.Div([
                    html.H5("Results by Thematic Area", className="mb-3 mt-0"),
                ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between"}, className="mb-3"),
                dcc.Graph(
                    id="petal-chart",
                    figure=petal_fig,
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'],
                        'toImageButtonOptions': {
                            'format': 'png', 
                            'filename': 'DRM_Assessment_Result',
                            'height': 800, 
                            'width': 800, 
                            'scale': 2
                        }
                    },
                    style={"maxWidth": "100%", "height": "auto", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"}
                ),
                dcc.Download(id="download-image")
            ])
            
            # Store the figure dict for download
            return {"display": "none"}, {"display": "block"}, petal_fig.to_dict(), figure_html, analysis_text, progress_fig, thematic_summaries
        except Exception as e:
            return {"display": "none"}, {"display": "block"}, None, html.Div([
                html.Div(f"Error generating figure: {str(e)}", className="alert alert-danger")
            ]), "", go.Figure(), []
