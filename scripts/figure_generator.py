"""
Figure Generator for DRM System Assessment
Converts input dataframe to PNG figure (base64 encoded)
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web applications

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import base64
from io import BytesIO

def generate_figure(df_input):
    """
    Generate DRM Assessment circular bar chart from input dataframe
    
    Args:
        df_input: DataFrame with DRM data (same structure as template)
        
    Returns:
        Base64 encoded PNG image string
    """
    
    # Process data similar to Example_Summary_Figure_clean.py
    df_raw = df_input.copy()
    
    # Remove completely empty rows
    df_raw = df_raw[df_raw["DRM Pillar"].notna() | df_raw["Thematic Area"].notna()].copy()
    
    # Create labels
    df_raw["individual"] = df_raw.apply(
        lambda row: row["Thematic Area"].strip() 
        if pd.notna(row["Thematic Area"]) and row["Thematic Area"].strip() != "-" 
        else row["DRM Pillar"] if pd.notna(row["DRM Pillar"]) else "", 
        axis=1
    )
    
    # Forward fill DRM Pillar to create groups
    df_raw["group"] = df_raw["DRM Pillar"].ffill()
    
    # Remove rows without labels
    df_raw = df_raw[df_raw["individual"] != ""].copy()
    
    # Get value columns (everything except DRM Pillar and Thematic Area)
    value_cols = [col for col in df_raw.columns if col not in ["DRM Pillar", "Thematic Area", "individual", "group"]]
    
    # Convert values to numeric and sum them
    for col in value_cols:
        df_raw[col] = pd.to_numeric(
            df_raw[col].astype(str).str.strip().replace("-", "0"), 
            errors='coerce',
            downcast='float'
        )
    
    # Calculate total value for each row
    df_raw["total_value"] = df_raw[value_cols].sum(axis=1)
    
    # Keep only needed columns
    df = df_raw[["individual", "group", "total_value"]].copy()
    df = df.sort_values(["group", "individual"]).reset_index(drop=True)
    
    # Remove leading numbers from names
    df["individual"] = df["individual"].str.replace(r'\d+', '', regex=True)
    df["individual"] = df["individual"].str.replace('.', '', regex=False)
    df["individual"] = df["individual"].str.strip()
    df["group"] = df["group"].str.replace(r'^\d+\.\s*', '', regex=True)
    df["individual"] = df["individual"].fillna("")
    
    # Calculate positions
    number_of_bars = len(df)
    number_of_groups = 6
    gap_width_ratio = 0.5
    
    bar_width = 2 * np.pi / (number_of_bars + number_of_groups * gap_width_ratio)
    gap_width = gap_width_ratio * bar_width
    
    # Create angles array with gaps between groups
    angles = []
    current_angle = 0.0
    
    for g in df["group"].unique():
        count = (df["group"] == g).sum()
        for _ in range(count):
            angles.append(current_angle)
            current_angle += bar_width
        current_angle += gap_width
    
    angles = np.array(angles)
    width = bar_width
    
    # Create circular bar chart
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location('N')
    
    # Get heights for bars
    heights = df["total_value"].values
    
    # Use viridis colormap
    cmap_gradient = plt.get_cmap('viridis')
    
    # Plot bars with vertical gradient based on absolute height (0-4 scale)
    max_scale = 4  # Maximum value on the scale
    
    for i, (angle, height) in enumerate(zip(angles, heights)):
        if height > 0:
            # Create stacked segments to simulate gradient
            n_segments = 50
            segment_height = height / n_segments
            
            for j in range(n_segments):
                # Color based on absolute height value (0 to 4)
                # Use center of segment for more accurate color
                absolute_position = ((j + 0.5) / n_segments) * height
                color_position = absolute_position / max_scale  # Normalize to 0-1 based on max scale
                color_position = min(color_position, 1.0)  # Cap at 1.0
                color = cmap_gradient(color_position)
                
                ax.bar(
                    angle, segment_height, 
                    width=width, 
                    bottom=j * segment_height, 
                    align="edge",
                    color=color, 
                    edgecolor=color, 
                    linewidth=0.5,
                    alpha=1.0,
                    zorder=10,
                )
    
    # Configure radial axis
    radial_ticks = [0, 1, 2, 3, 4]
    max_value = df["total_value"].max()
    ax.set_ylim(-0.5, max(max_value * 1.2, 4))
    ax.set_yticks(radial_ticks)
    ax.set_yticklabels([str('') for r in radial_ticks], fontsize=10, color="grey")
    ax.yaxis.grid(True, color="grey", linestyle=(0, (4, 6)), linewidth=1, zorder=0, alpha=0.2)
    ax.set_xticks([])
    
    # Add group labels
    title_texts = ['Legal and\nInstitutional\nDRM Framework', 'Risk\nIdentification', 'Risk\nReduction',
                   'Preparedness', 'Financial\nProtection', 'Resilient\nReconstruction']
    
    group_positions = {}
    idx = 0
    for g in df["group"].unique():
        count = (df["group"] == g).sum()
        start = idx
        end = idx + count - 1
        group_positions[g] = (start, end)
        idx += count
    
    i = 0
    for g, (start, end) in group_positions.items():
        theta_start = angles[start] if start < len(angles) else angles[-1]
        theta_end = angles[end] + width if end < len(angles) else angles[-1] + width
        
        max_radius = max(max_value * 1.2, 4)
        separator_theta = angles[end] + width + gap_width / 2
        ax.plot([separator_theta, separator_theta], [0, max_radius], 
                color='gray', linewidth=1, alpha=0.2, zorder=15)
        
        ax.text(
            (theta_start + theta_end) / 2, 4.7, title_texts[i],
            ha='center', va='center',
            fontsize=8, fontweight='bold', alpha=0.9
        )
        i += 1
    
    # Add individual bar labels
    d = {'DRM policies and institutions': 'DRM policies\nand\ninstitutions',
         'Mainstreaming DRM into national and sectoral development plans': 'Mainstreaming\nDRM into\nnational and\nsectoral\ndevelopment\nplans',
         'Risk identification': 'Risk\nidentification',
         'Territorial and urban planning': 'Territorial\nand\nurban\nplanning',
         'Public investment at the central level': 'Public\ninvestment at\nthe central\nlevel',
         'Sector-specific risk reduction measures': 'Sector-specific\nrisk\nreduction\nmeasures',
         'Early warning systems': 'Early\nwarning\nsystems',
         'Emergency preparedness and response': 'Emergency\npreparedness\n& response',
         'Adaptive social protection': 'Adaptive\nsocial\nprotection',
         'Fiscal risk management': 'Fiscal risk\nmanagement',
         'DRF strategies and instruments': 'DRF strategies\nand\ninstruments',
         'Resilient reconstruction': 'Resilient\nreconstruction'}
    
    for old, new in d.items():
        df["individual"] = df["individual"].astype(str).str.replace(old, new, regex=False)
    
    for i, row in df.iterrows():
        angle = angles[i] + width / 2
        total_y = row["total_value"]
        name = row["individual"]
        c = "black"
        if total_y < 1:
            c = "red"
        
        if total_y < 2:
            total_y = 2
        
        if name:
            rotation = np.degrees(-angle)
            va = "bottom"
            
            if -270 < rotation < -90:
                rotation += 180
                total_y += 0.1
                va = "top"
            
            ax.text(
                angle, total_y, name, 
                rotation=rotation, 
                rotation_mode="anchor",
                ha="center", 
                va=va,
                fontsize=7, 
                alpha=0.7, 
                fontweight="bold",
                color=c,
            )
    
    ax.set_frame_on(False)
    
    # Add standard circles with labels
    theta_circle = np.linspace(0, 2 * np.pi, 100)
    r_circle = np.ones_like(theta_circle)
    
    # Circle at 1...
    ax.plot(theta_circle, r_circle, color='red', linewidth=1, zorder=5, linestyle='--', label="Nascent", alpha=0.5)
    ax.plot(theta_circle, 2 * r_circle, color='orange', linewidth=1, zorder=5, linestyle='--', label="Emerging", alpha=0.5)
    ax.plot(theta_circle, 3 * r_circle, color='blue', linewidth=1, zorder=5, linestyle='--', label="Established", alpha=0.5)
    ax.plot(theta_circle, 4 * r_circle, color='green', linewidth=1, zorder=5, linestyle='--', label="Mature", alpha=0.5)
    
    # Add legend
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.1), ncols=4, fontsize=8, frameon=False)
    plt.subplots_adjust(top=0.95, bottom=0.15)
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close(fig)
    
    return image_base64
