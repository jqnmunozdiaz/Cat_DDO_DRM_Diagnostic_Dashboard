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
    
    # Reference circle configs
    circle_configs = [
        (1, '#e74c3c', 'Nascent'),      # Red
        (2, '#e67e22', 'Emerging'),      # Orange  
        (3, '#3498db', 'Established'),   # Blue
        (4, '#27ae60', 'Mature'),        # Green
    ]
    
    # Add reference circles as thin Barpolar rings FIRST (so they render behind data bars)
    # Using Barpolar ensures same rendering layer as data bars
    circle_angles_deg = np.linspace(0, 360, 72, endpoint=False)  # 72 segments for smooth circle
    ring_width = 0.02  # Very thin ring
    
    for radius, color, name in circle_configs:
        fig.add_trace(go.Barpolar(
            r=[ring_width] * len(circle_angles_deg),
            theta=circle_angles_deg,
            width=[5] * len(circle_angles_deg),
            base=[radius - ring_width/2] * len(circle_angles_deg),
            marker=dict(
                color=color,
                line=dict(width=0.5, color=color)
            ),
            opacity=0.4,
            name=name,
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add bars - batch segments by color level for efficiency
    n_segments = 50  # Reduced for performance, overlap fixes appearance
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
    
    # Add invisible traces for legend (shapes don't appear in legend)
    for radius, color, name in circle_configs:
        fig.add_trace(go.Scatterpolar(
            r=[None],
            theta=[None],
            mode='lines',
            line=dict(color=color, width=1.5, dash='solid'),
            name=name,
            showlegend=True
        ))
    
    # Calculate scale factor dynamically based on radial axis range and layout
    # With margins of 40px on 800px height, plot domain is from 0.05 to 0.95 in paper coords
    # That's 0.9 total, so radius from center to edge is 0.45 in paper coordinates
    max_radius = 5  # Must match the radialaxis range max value
    height = 800
    margin = 40
    # Plot domain fraction = (height - 2*margin) / height = (800-80)/800 = 0.9
    # Half of that (radius in paper coords) = 0.45
    plot_radius_fraction = (height - 2 * margin) / height / 2  # = 0.45
    scale_factor = plot_radius_fraction / max_radius  # = 0.09
    
    # Add pillar group labels
    title_texts = [
        'Legal and<br>Institutional<br>DRM Framework', 
        'Risk<br>Identification', 
        'Risk<br>Reduction',
        'Preparedness', 
        'Financial<br>Protection', 
        'Resilient<br>Reconstruction'
    ]
    
    for i, (pillar, (start_idx, end_idx, theta_start, theta_end)) in enumerate(group_positions.items()):
        mid_angle = (theta_start + theta_end) / 2
        # Position labels outside the chart
        label_radius = 5.9
        x_pos = 0.5 + (label_radius * scale_factor) * np.cos(np.radians(90 - mid_angle))
        y_pos = 0.5 + (label_radius * scale_factor) * np.sin(np.radians(90 - mid_angle))

        # Manual adjustment for "Legal and Institutional" (index 0)
        if i == 0:
            x_pos += 0.03
        
        fig.add_annotation(
            x=x_pos,
            y=y_pos,
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
        text_color = 'red' if score < 1 else '#333'
        
        # Position label just outside the bar (minimum radius of 2 for visibility)
        # Add offset to place label center outside the bar
        label_radius = max(2, score) + 0.5
        
        # Calculate marker size based on text dimensions (approximation)
        lines = display_name.split('<br>')
        max_line_chars = max(len(line) for line in lines)
        # Use max of width and height estimates for circular marker
        marker_size = max_line_chars * 3
        
        # Add white square marker as background (uses polar coordinates - will align!)
        fig.add_trace(go.Scatterpolar(
            r=[label_radius],
            theta=[angle],
            mode='markers',
            marker=dict(
                size=marker_size,
                symbol='circle',
                color='rgba(255, 255, 255, 0.9)',
                line=dict(width=0)
            ),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add text on top (same polar coordinates - guaranteed alignment)
        fig.add_trace(go.Scatterpolar(
            r=[label_radius],
            theta=[angle],
            mode='text',
            text=[display_name],
            textposition='middle center',
            textfont=dict(size=8, color=text_color, family='Arial'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add a white filled circle at the center to create a "donut" look
    center_hole_radius = 0.35
    fig.add_trace(go.Scatterpolar(
        r=[center_hole_radius] * 72,
        theta=np.linspace(0, 360, 72, endpoint=False),
        mode='lines',
        fill='toself',
        fillcolor='white',
        line=dict(color='white', width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

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
        plot_bgcolor='white',  # Set plot area background to white
        autosize=True,  # Responsive width
        height=800,  # Increased height
        margin=dict(l=40, r=40, t=40, b=40),
        dragmode=False  # Disable zoom/pan
    )
    
    return fig
