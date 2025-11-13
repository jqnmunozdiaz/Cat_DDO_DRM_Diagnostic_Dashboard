"""
Figure Generator for DRM System Assessment
Converts input dataframe to PNG figure (base64 encoded)
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web applications

import numpy as np
import pandas as pd
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
    
    # Process data similar to Example_Summary_Figure_clean.py
    df_raw = df_input.copy()
    
    # Remove completely empty rows
    df_raw = df_raw[df_raw["DRM Pillar"].notna() | df_raw["Thematic Area"].notna()].copy()
    
    # Define the assessment category columns
    value_cols = [col for col in df_raw.columns if col not in ["DRM Pillar", "Thematic Area"]]
    
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
    
    # Convert values to numeric
    for col in value_cols:
        df_raw[col] = pd.to_numeric(
            df_raw[col].astype(str).str.strip().replace("-", "0"), 
            errors='coerce',
            downcast='float'
        )
    
    # Keep only needed columns
    df = df_raw[["individual", "group"] + value_cols].copy()
    df = df.sort_values(["group", "individual"]).reset_index(drop=True)
    
    # Reshape to long format
    df_long = df.melt(
        id_vars=["individual", "group"], 
        value_vars=value_cols,
        var_name="observation", 
        value_name="value"
    )
    
    obs_types = len(value_cols)
    df_long = df_long.sort_values(["group", "individual"]).reset_index(drop=True)
    
    # Assign unique ID to each bar position
    ids = np.repeat(np.arange(1, int(df_long.shape[0] / obs_types) + 1), obs_types)
    df_long = df_long.iloc[:len(ids)].copy()
    df_long["id"] = ids
    
    # Remove leading numbers from names
    df_long["individual"] = df_long["individual"].str.replace(r'\d+', '', regex=True)
    df_long["individual"] = df_long["individual"].str.replace('.', '', regex=False)
    df_long["individual"] = df_long["individual"].str.strip()
    df_long["group"] = df_long["group"].str.replace(r'^\d+\.\s*', '', regex=True)
    
    # Create label data
    label_data = df_long.groupby(["id", "individual"], sort=False)["value"].sum().reset_index()
    label_data["individual"] = label_data["individual"].fillna("")
    
    # Calculate positions
    number_of_bars = len(label_data)
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
    
    # Get colors for each category
    cmap = plt.get_cmap("viridis", len(value_cols))
    
    # Plot each category as a stacked layer
    for i, (obs, color) in enumerate(zip(value_cols, cmap(np.linspace(0, 1, len(value_cols))))):
        obs_df = df_long[df_long["observation"] == obs].copy()
        
        heights = []
        for idx in range(1, number_of_bars + 1):
            subset = obs_df[obs_df["id"] == idx]
            val = subset["value"].values[0] if len(subset) else 0
            heights.append(0 if np.isnan(val) else val)
        heights = np.array(heights)
        
        if i == 0:
            bottom = np.zeros_like(heights)
        else:
            bottom = bottom + prev_heights
        
        ax.bar(
            angles, heights, 
            width=width, 
            bottom=bottom, 
            align="edge",
            color=color, 
            edgecolor="none", 
            alpha=0.9, 
            label=obs,
            zorder=10,
        )
        
        prev_heights = heights
    
    # Configure radial axis
    radial_ticks = [0, 1, 2, 3, 4]
    max_value = df_long.groupby("id")["value"].sum().max()
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
        label_data["individual"] = label_data["individual"].astype(str).str.replace(old, new, regex=False)
    
    for i, row in label_data.iterrows():
        angle = angles[i] + width / 2
        total_y = df_long[df_long["id"] == (i + 1)]["value"].sum(skipna=True)
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
    
    # Add minimum standard circle
    theta_circle = np.linspace(0, 2 * np.pi, 100)
    r_circle = np.ones_like(theta_circle)
    ax.plot(theta_circle, r_circle, color='red', linewidth=1, zorder=5, linestyle='--', label="Minimum standard")
    
    # Finalize legend
    handles, labels = ax.get_legend_handles_labels()
    if "Minimum standard" in labels:
        i = labels.index("Minimum standard")
        h = handles.pop(i)
        l = labels.pop(i)
        insert_pos = 1 if len(labels) >= 1 else 0
        handles.insert(insert_pos, h)
        labels.insert(insert_pos, l)
    
    ax.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, -0.1), ncols=4, fontsize=8, frameon=False)
    plt.subplots_adjust(top=0.95, bottom=0.15)
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close(fig)
    
    return image_base64
