"""
Figure Generator for DRM System Assessment - Plotly Version
Generates interactive polar bar chart using Plotly for fast client-side rendering
"""

import numpy as np
import plotly.graph_objects as go
import plotly.colors as pc

# Viridis colorscale values for manual color mapping
VIRIDIS_COLORS = [
    (0.0, '#440154'), (0.25, '#3b528b'), (0.5, '#21918c'), 
    (0.75, '#5ec962'), (1.0, '#fde725')
]

def get_viridis_color(value):
    """Get viridis color for a value between 0-1"""
    colors = pc.sample_colorscale('Viridis', [value])[0]
    return colors

def generate_figure(df_input):
    """
    Generate DRM Assessment circular bar chart using Plotly barpolar
    
    Args:
        df_input: DataFrame with DRM data columns: "DRM Pillar", "Thematic Area", "Score" (0-1)
        
    Returns:
        Plotly Figure object
    """
    
    df = df_input.copy()
    
    # Scale normalized scores (0-1) to chart scale (0-4)
    max_scale = 4
    df["Score"] = df["Score"] * max_scale
    
    # Clean thematic area names for display
    df["Thematic Area Clean"] = df["Thematic Area"].str.replace(r'^\d+\.\d*\.?\s*', '', regex=True).str.strip()
    df["DRM Pillar Clean"] = df["DRM Pillar"].str.replace(r'^\d+\.\s*', '', regex=True)
    
    # Calculate bar positions with gaps between groups
    number_of_bars = len(df)
    number_of_groups = 6
    gap_width_ratio = 0.5
    
    bar_width_deg = 360 / (number_of_bars + number_of_groups * gap_width_ratio)
    gap_width_deg = gap_width_ratio * bar_width_deg
    
    # Build angles with gaps between groups
    angles = []
    current_angle = 0.0
    group_positions = {}  # Store start/end for each group
    
    for g in df["DRM Pillar"].unique():
        count = (df["DRM Pillar"] == g).sum()
        start_idx = len(angles)
        for _ in range(count):
            angles.append(current_angle)
            current_angle += bar_width_deg
        end_idx = len(angles) - 1
        group_positions[g] = (start_idx, end_idx, angles[start_idx], angles[end_idx] + bar_width_deg)
        current_angle += gap_width_deg
    
    df["angle"] = angles
    
    # Create figure
    fig = go.Figure()
    
    # Add bars - batch segments by color level for efficiency
    n_segments = 20  # Reduced for performance, overlap fixes appearance
    overlap = 0.02  # Small overlap to eliminate white gaps
    
    # Group all segments by their color level (across all bars)
    for j in range(n_segments):
        r_values = []
        theta_values = []
        width_values = []
        base_values = []
        colors = []
        line_colors = []
        
        for idx, row in df.iterrows():
            angle = row["angle"]
            height = row["Score"]
            
            if height > 0:
                segment_height = height / n_segments
                bottom = j * segment_height
                
                # Only add segment if it's within the bar's height
                if bottom < height:
                    # Add small overlap to prevent white gaps
                    actual_segment = min(segment_height + overlap, height - bottom + overlap)
                    absolute_position = ((j + 0.5) / n_segments) * height
                    color_position = min(absolute_position / max_scale, 1.0)
                    color = get_viridis_color(color_position)
                    
                    r_values.append(actual_segment)
                    theta_values.append(angle + bar_width_deg / 2)
                    width_values.append(bar_width_deg * 0.95)
                    base_values.append(bottom)
                    colors.append(color)
                    line_colors.append(color)
        
        if r_values:
            fig.add_trace(go.Barpolar(
                r=r_values,
                theta=theta_values,
                width=width_values,
                base=base_values,
                marker=dict(color=colors, line=dict(width=0.5, color=line_colors)),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Add gray separator lines between pillar groups
    max_radius = 4.4
    for pillar, (start_idx, end_idx, theta_start, theta_end) in group_positions.items():
        separator_angle = theta_end + gap_width_deg / 2
        fig.add_trace(go.Scatterpolar(
            r=[0, max_radius],
            theta=[separator_angle, separator_angle],
            mode='lines',
            line=dict(color='lightgray', width=1, dash='solid'),
            showlegend=False,
            hoverinfo='skip',
            opacity=0.5
        ))
    # Add reference circles
    circle_angles = np.linspace(0, 360, 100, endpoint=False)
    
    circle_configs = [
        (1, '#e74c3c', 'Nascent'),      # Red
        (2, '#e67e22', 'Emerging'),      # Orange  
        (3, '#3498db', 'Established'),   # Blue
        (4, '#27ae60', 'Mature'),        # Green
    ]
    
    for radius, color, name in circle_configs:
        fig.add_trace(go.Scatterpolar(
            r=[radius] * len(circle_angles),
            theta=circle_angles,
            mode='lines',
            line=dict(color=color, width=1.5, dash='dash'),
            name=name,
            showlegend=True,
            hoverinfo='skip'
        ))
    
    # Add pillar group labels
    title_texts = [
        'Legal and\nInstitutional\nDRM Framework', 
        'Risk\nIdentification', 
        'Risk\nReduction',
        'Preparedness', 
        'Financial\nProtection', 
        'Resilient\nReconstruction'
    ]
    
    for i, (pillar, (start_idx, end_idx, theta_start, theta_end)) in enumerate(group_positions.items()):
        mid_angle = (theta_start + theta_end) / 2
        # Position labels outside the chart
        label_radius = 5.3
        
        fig.add_annotation(
            x=0.5 + 0.42 * np.cos(np.radians(90 - mid_angle)),
            y=0.5 + 0.42 * np.sin(np.radians(90 - mid_angle)),
            text=title_texts[i],
            showarrow=False,
            font=dict(size=10, color='#333', family='Arial Black'),
            align='center',
            xref='paper',
            yref='paper'
        )
    
    # Add individual bar labels
    label_mapping = {
        'DRM policies and institutions': 'DRM policies<br>and institutions',
        'Mainstreaming DRM into national and sectoral development plans': 'Mainstreaming DRM<br>into national and<br>sectoral plans',
        'Risk identification': 'Risk<br>identification',
        'Territorial and urban planning': 'Territorial and<br>urban planning',
        'Public investment at the central level': 'Public investment<br>at central level',
        'Sector-specific risk reduction measures': 'Sector-specific<br>risk reduction',
        'Early warning systems': 'Early warning<br>systems',
        'Emergency preparedness and response': 'Emergency<br>preparedness',
        'Adaptive social protection': 'Adaptive social<br>protection',
        'Fiscal risk management': 'Fiscal risk<br>management',
        'DRF strategies and instruments': 'DRF strategies<br>and instruments',
        'Resilient reconstruction': 'Resilient<br>reconstruction'
    }
    
    for idx, row in df.iterrows():
        angle = row["angle"] + bar_width_deg / 2
        score = row["Score"]
        name = row["Thematic Area Clean"]
        
        # Map to shorter label if available
        display_name = label_mapping.get(name, name.replace(' ', '<br>'))
        
        # Color red if below minimum standard
        text_color = '#c0392b' if score < 1 else '#333'
        
        # Position label at end of bar (minimum at 2 for readability)
        label_radius = max(score + 0.3, 2.3)
        
        # Calculate rotation like matplotlib: rotation = -angle (in degrees)
        # Plotly uses clockwise from top, matplotlib uses counterclockwise from right
        rotation = -angle  # Angle is already in degrees
        
        # Flip text for bottom half of chart (like matplotlib)
        if -270 < rotation < -90:
            rotation += 180
            label_radius += 0.1
        
        # Convert polar to cartesian for annotation
        angle_rad = np.radians(90 - angle)  # Convert to standard coordinates
        x_pos = 0.5 + (label_radius / 6.5) * np.cos(angle_rad)
        y_pos = 0.5 + (label_radius / 6.5) * np.sin(angle_rad)
        
        fig.add_annotation(
            x=x_pos,
            y=y_pos,
            text=display_name,
            showarrow=False,
            font=dict(size=8, color=text_color, family='Arial'),
            align='center',
            xref='paper',
            yref='paper',
            textangle=-rotation,  # Plotly uses opposite sign convention
            bgcolor='rgba(255,255,255,0.85)',
            borderpad=2
        )
    
    # Configure layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                showticklabels=False,
                showline=False,
                showgrid=False  # Remove all radial grid lines
            ),
            angularaxis=dict(
                visible=False,
                direction='clockwise',
                rotation=90
            ),
            bgcolor='white'
        ),
        showlegend=True,
        legend=dict(
            x=1.0,
            y=1.0,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#ddd',
            borderwidth=1,
            font=dict(size=10)
        ),
        paper_bgcolor='white',
        autosize=True,  # Responsive width
        height=800,  # Increased height
        margin=dict(l=40, r=40, t=40, b=40),
        dragmode=False  # Disable zoom/pan
    )
    
    return fig


def generate_figure_base64(df_input):
    """
    Legacy function: Generate base64 PNG from Plotly figure
    Used for download functionality
    """
    fig = generate_figure(df_input)
    img_bytes = fig.to_image(format="png", width=800, height=800, scale=2)
    import base64
    return base64.b64encode(img_bytes).decode()
