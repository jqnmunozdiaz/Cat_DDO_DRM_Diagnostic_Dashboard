"""
Figure Generator for DRM System Assessment
Converts input dataframe to PNG figure (base64 encoded)
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web applications

import numpy as np
import matplotlib.pyplot as plt
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
    
    # Process dataframe - input has "DRM Pillar", "Thematic Area", "Score" (normalized 0-1)
    df = df_input.copy()
    
    # Scale normalized scores (0-1) to chart scale (0-4)
    max_scale = 4  # Maximum value on the scale
    df["Score"] = df["Score"] * max_scale
    
    # Remove leading numbers from names for display
    df["Thematic Area"] = df["Thematic Area"].str.replace(r'\d+', '', regex=True)
    df["Thematic Area"] = df["Thematic Area"].str.replace('.', '', regex=False)
    df["Thematic Area"] = df["Thematic Area"].str.strip()
    df["DRM Pillar"] = df["DRM Pillar"].str.replace(r'^\d+\.\s*', '', regex=True)
    df["Thematic Area"] = df["Thematic Area"].fillna("")
    
    # Calculate positions
    number_of_bars = len(df)
    number_of_groups = 6
    gap_width_ratio = 0.5
    
    bar_width = 2 * np.pi / (number_of_bars + number_of_groups * gap_width_ratio)
    gap_width = gap_width_ratio * bar_width
    
    # Create angles array with gaps between groups
    angles = []
    current_angle = 0.0
    
    for g in df["DRM Pillar"].unique():
        count = (df["DRM Pillar"] == g).sum()
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
    heights = df["Score"].values
    
    # Use viridis colormap
    cmap_gradient = plt.get_cmap('viridis')
    
    # Plot bars with vertical gradient based on absolute height (0-4 scale)
    
    for i, (angle, height) in enumerate(zip(angles, heights)):
        # Draw full background bar (transparent with white border)
        ax.bar(
            angle, height,
            width=width,
            bottom=0,
            align="edge",
            facecolor='none',
            edgecolor='white',
            linewidth=0.5,
            zorder=11,
        )
        
        if height > 0:
            # Create stacked segments to simulate gradient
            n_segments = 200
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
    max_value = df["Score"].max()
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
    for g in df["DRM Pillar"].unique():
        count = (df["DRM Pillar"] == g).sum()
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
        
        # Determine title distance based on max score in this group
        group_max_score = df[df["DRM Pillar"] == g]["Score"].max()
        title_distance = 5.2 if group_max_score >= 4 else 4.7
        
        ax.text(
            (theta_start + theta_end) / 2, title_distance, title_texts[i],
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
        df["Thematic Area"] = df["Thematic Area"].astype(str).str.replace(old, new, regex=False)
    
    for i, row in df.iterrows():
        angle = angles[i] + width / 2
        total_y = row["Score"]
        name = row["Thematic Area"]
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
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.9),
                zorder=9
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
    ax.legend(loc="upper right", ncols=1, fontsize=8, frameon=True, borderpad=1.2, labelspacing=0.8)
    plt.subplots_adjust(top=0.95, bottom=0.15)
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close(fig)
    
    return image_base64
