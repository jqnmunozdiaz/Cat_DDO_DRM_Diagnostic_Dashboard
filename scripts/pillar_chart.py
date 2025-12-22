"""
Generate pillar progress bar chart
"""

import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

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
        # Simple average: each thematic area contributes equally to pillar score
        avg_score = pillar_rows["Score"].mean()
        # Convert to percentage for display
        pillar_scores[pillar] = avg_score * 100
    
    # Create horizontal progress bars using Plotly
    pillars = list(pillar_scores.keys())
    scores = [pillar_scores[p] for p in pillars]
    
    # Remove leading numbers from pillar names for display
    pillar_labels = [p.split('. ', 1)[1] if '. ' in p else p for p in pillars]
    
    # Use viridis colormap for continuous colors based on score (0-100)
    cmap = plt.get_cmap('viridis')
    colors = []
    text_colors = []
    for score in scores:
        # Normalize score (0-100) to colormap range (0-1)
        color_position = score / 100
        rgba = cmap(color_position)
        # Convert matplotlib RGBA to hex color for Plotly
        hex_color = mcolors.to_hex(rgba)
        colors.append(hex_color)
        # Red text if below 25%
        text_colors.append('red' if score < 25 else 'black')
    
    # Apply text colors to pillar labels
    colored_labels = [
        f'<span style="color:{tc}">{label}</span>' 
        for label, tc in zip(pillar_labels, text_colors)
    ]
    
    progress_fig = go.Figure()
    
    progress_fig.add_trace(go.Bar(
        y=colored_labels,
        x=scores,
        orientation='h',
        marker=dict(color=colors),
        hoverinfo='none',
        hovertemplate=None
    ))
    
    progress_fig.update_layout(
        xaxis=dict(
            title="Achievement",
            range=[0, 105],  # Extended slightly beyond 100 to show the 100% gridline
            showgrid=True,
            gridcolor='lightgray',
            tickmode='array',
            tickvals=[0, 25, 50, 75, 100],
            ticktext=['-', 'Nascent', 'Emerging', 'Established', 'Mature']
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
