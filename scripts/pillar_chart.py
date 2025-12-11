"""
Generate pillar progress bar chart
"""

import plotly.graph_objects as go
import pandas as pd

def generate_pillar_chart(df: pd.DataFrame) -> go.Figure:
    """
    Generate horizontal progress bars showing achievement by DRM pillar.
    
    Args:
        df: DataFrame with columns 'DRM Pillar', 'Thematic Area', and 'Score' (0-1 normalized)
        
    Returns:
        Plotly Figure object with horizontal bar chart
    """
    # Calculate average achievement per pillar (scores are already normalized 0-1)
    pillar_scores = {}
    for pillar in df["DRM Pillar"].unique():
        pillar_rows = df[df["DRM Pillar"] == pillar]
        # Average of thematic area scores within this pillar
        avg_score = pillar_rows["Score"].mean()
        # Convert to percentage for display
        pillar_scores[pillar] = avg_score * 100
    
    # Create horizontal progress bars using Plotly
    pillars = list(pillar_scores.keys())
    scores = [pillar_scores[p] for p in pillars]
    
    # Determine colors based on score (red if <25%, orange if <50%, yellow if <75%, blue if >=75%)
    colors = []
    for score in scores:
        if score < 25:
            colors.append('#dc3545')  # red
        elif score < 50:
            colors.append('#fd7e14')  # orange
        elif score < 75:
            colors.append('#ffc107')  # yellow
        else:
            colors.append('#0d6efd')  # blue
    
    progress_fig = go.Figure()
    
    progress_fig.add_trace(go.Bar(
        y=pillars,
        x=scores,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{s:.0f}%" for s in scores],
        textposition='outside',
        hoverinfo='none',
        hovertemplate=None
    ))
    
    progress_fig.update_layout(
        xaxis=dict(
            title="Achievement (%)",
            range=[0, 100],
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title="",
            autorange="reversed"
        ),
        height=max(300, len(pillars) * 60),
        margin=dict(l=20, r=80, t=20, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return progress_fig
