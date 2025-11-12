"""
DRM System Assessment Circular Bar Chart
Creates a circular (polar) stacked bar chart visualizing DRM assessment data
"""

import numpy as np
import pandas as pd
import textwrap
import matplotlib.pyplot as plt

# =============================================================================
# 1. DATA LOADING AND PREPROCESSING
# =============================================================================

# Load CSV data
df_raw = pd.read_csv("data/DRM_system_assessment_template_filled_example.csv")

# Remove completely empty rows
df_raw = df_raw[df_raw["DRM Pillar"].notna() | df_raw["DRM sub-pillar"].notna()].copy()


# Define the assessment category columns (these will be the stacked colors)
# Retrieve value columns dynamically from the CSV, excluding known non-value columns
value_cols = [col for col in df_raw.columns if col not in ["DRM Pillar", "DRM sub-pillar"]]

# Create labels: use sub-pillar if available, otherwise use pillar name
df_raw["individual"] = df_raw.apply(
    lambda row: row["DRM sub-pillar"].strip() 
    if pd.notna(row["DRM sub-pillar"]) and row["DRM sub-pillar"].strip() != "-" 
    else row["DRM Pillar"] if pd.notna(row["DRM Pillar"]) else "", 
    axis=1
)

# Forward fill DRM Pillar to create groups
df_raw["group"] = df_raw["DRM Pillar"].ffill()

# Remove rows without labels
df_raw = df_raw[df_raw["individual"] != ""].copy()

# Convert values to numeric (0-1 scale), replace "-" with NaN, ensure float dtype
for col in value_cols:
    df_raw[col] = pd.to_numeric(
        df_raw[col].astype(str).str.strip().replace("-", "0"), 
        errors='coerce',
        downcast='float'
    )

# Keep only needed columns
df = df_raw[["individual", "group"] + value_cols].copy()

# Merge 3.3.a and 3.3.b Sector-specific risk reduction measures
# Check if both exist and average their values
mask_3_3_a = df["individual"].str.contains("3.3.a", na=False, regex=False)
mask_3_3_b = df["individual"].str.contains("3.3.b", na=False, regex=False)

if mask_3_3_a.any() and mask_3_3_b.any():
    # Get the rows for 3.3.a and 3.3.b
    row_3_3_a = df[mask_3_3_a].copy()
    row_3_3_b = df[mask_3_3_b].copy()
    
    # Average the value columns
    for col in value_cols:
        row_3_3_a[col] = (row_3_3_a[col].values + row_3_3_b[col].values) / 2
    
    # Update the label to remove .a
    row_3_3_a["individual"] = row_3_3_a["individual"].str.replace("3.3.a", "3.3", regex=False)
    
    # Remove both 3.3.a and 3.3.b from df
    df = df[~(mask_3_3_a | mask_3_3_b)].copy()
    
    # Add back the merged row
    df = pd.concat([df, row_3_3_a], ignore_index=True)
    
    # Re-sort by group
    df = df.sort_values(["group", "individual"]).reset_index(drop=True)

# =============================================================================
# 2. DATA RESHAPING FOR PLOTTING
# =============================================================================

# Reshape from wide to long format
df_long = df.melt(
    id_vars=["individual", "group"], 
    value_vars=value_cols,
    var_name="observation", 
    value_name="value"
)

# Sort by group and individual
obs_types = len(value_cols)
df_long = df_long.sort_values(["group", "individual"]).reset_index(drop=True)

# Assign unique ID to each bar position
ids = np.repeat(np.arange(1, int(df_long.shape[0] / obs_types) + 1), obs_types)
df_long = df_long.iloc[:len(ids)].copy()
df_long["id"] = ids

# Remove leading numbers (e.g., "1. ") from individual and group names
df_long["individual"] = df_long["individual"].str.replace(r'\d+', '', regex=True)
df_long["individual"] = df_long["individual"].str.replace('.', '')
df_long["individual"] = df_long["individual"].str.strip()
df_long["group"] = df_long["group"].str.replace(r'^\d+\.\s*', '', regex=True)

# =============================================================================
# 3. PREPARE PLOTTING DATA
# =============================================================================

# Create label data (one row per bar)
label_data = df_long.groupby(["id", "individual"], sort=False)["value"].sum().reset_index()
label_data["individual"] = label_data["individual"].fillna("")

# Calculate positions with manual spacing control
number_of_bars = len(label_data)
number_of_groups = 6
gap_width_ratio = 0.5  # Width of gap relative to bar width

# Calculate bar width accounting for gaps
# Total circle = bars + gaps
# If we have n bars and g gaps, and gap = r * bar_width:
# 2π = n * bar_width + g * r * bar_width
# bar_width = 2π / (n + g * r)
bar_width = 2 * np.pi / (number_of_bars + number_of_groups * gap_width_ratio)
gap_width = gap_width_ratio * bar_width

# Create angles array with gaps between groups
# Build angles manually based on group membership
# Start at 0 and go counter-clockwise (matplotlib will handle the rotation and direction)
angles = []
current_angle = 0.0

for g in df["group"].unique():
    count = (df["group"] == g).sum()
    # Add bars for this group (no gaps within group)
    for _ in range(count):
        angles.append(current_angle)
        current_angle += bar_width
    # Add gap after this group (except after the last group)
    current_angle += gap_width

angles = np.array(angles)
width = bar_width

# =============================================================================
# 4. CREATE CIRCULAR BAR CHART
# =============================================================================

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# Set theta direction to clockwise and start at top (90 degrees)
ax.set_theta_direction(-1)  # -1 for clockwise
ax.set_theta_zero_location('N')  # 'N' for North (top, 90 degrees)
# ax.set_theta_offset(np.deg2rad(0.001))   # clockwise

# Get colors for each category
cmap = plt.get_cmap("viridis", len(value_cols))

# Plot each category as a stacked layer
for i, (obs, color) in enumerate(zip(value_cols, cmap(np.linspace(0, 1, len(value_cols))))):
    obs_df = df_long[df_long["observation"] == obs].copy()
    
    # Extract heights for each bar position
    heights = []
    for idx in range(1, number_of_bars + 1):
        subset = obs_df[obs_df["id"] == idx]
        val = subset["value"].values[0] if len(subset) else 0
        heights.append(0 if np.isnan(val) else val)
    heights = np.array(heights)
    
    # Calculate bottom position (stacking)
    if i == 0:
        bottom = np.zeros_like(heights)
    else:
        bottom = bottom + prev_heights
    
    # Draw bars (full width, no additional spacing since we manually control gaps)
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

# =============================================================================
# 5. CONFIGURE RADIAL AXIS
# =============================================================================

radial_ticks = [0, 1, 2, 3, 4]
max_value = df_long.groupby("id")["value"].sum().max()
# Create empty space in center by setting negative lower limit
ax.set_ylim(-0.5, max(max_value * 1.2, 4))
ax.set_yticks(radial_ticks)
ax.set_yticklabels([str('') for r in radial_ticks], fontsize=10, color="grey")
ax.yaxis.grid(True, color="grey", linestyle= (0, (4, 6)), linewidth=1, zorder=0, alpha=0.2)
ax.set_xticks([])

# =============================================================================
# 6. ADD GROUP LABELS (DRM Pillars)
# =============================================================================

title_texts = ['Legal and\nInstitutional\nDRM Framework', 'Risk\nIdentification', 'Risk\nReduction',
               'Preparedness', 'Financial\nProtection', 'Resilient\nReconstruction']

# Calculate position range for each group
group_positions = {}
idx = 0
for g in df["group"].unique():
    count = (df["group"] == g).sum()
    start = idx
    end = idx + count - 1
    group_positions[g] = (start, end)
    idx += count

# Draw group labels (base lines and curved text in center space)
i=0
for g, (start, end) in group_positions.items():

    theta_start = angles[start] if start < len(angles) else angles[-1]
    # Add width to end position to cover the full bar (since bars use align="edge")
    theta_end = angles[end] + width if end < len(angles) else angles[-1] + width
    # Draw base line beneath the bars (closer to bars, not in center)
    theta_mid = np.linspace(theta_start*1.05, theta_end*0.95, 100)
    
    # Draw separator line at the end of each group (in the middle of the gap)
    
    max_radius = max(max_value * 1.2, 4)
    # Position line in the center of the gap after this group
    separator_theta = angles[end] + width + gap_width / 2
    ax.plot([separator_theta, separator_theta], [0, max_radius], 
            color='gray', linewidth=1, alpha=0.2, zorder=15)
    
    # Add curved group label text in the center empty space
    ax.text(
        (theta_start + theta_end) / 2, 4.7, title_texts[i],
        ha='center', va='center',
        fontsize=8, fontweight='bold', alpha=0.9
    )
    i += 1

# =============================================================================
# 7. ADD INDIVIDUAL BAR LABELS (Sub-pillars)
# =============================================================================

d = {'DRM policies and institutions': 'DRM policies\nand\ninstitutions',
     'DRM in national and sectoral development plans': 'DRM in\nnational and\nsectoral\ndevelopment\nplans',
     'Risk Identification': 'Risk\nIdentification',
     'Territorial and urban planning': 'Territorial\nand\nurban\nplanning',
     'Public investment at the central level': 'Public\ninvestment at\nthe central\nlevel',
     'Sector-specific risk reduction measures': 'Sector-specific\nrisk\nreduction\nmeasures',
     'EWS': 'EWS',
     'EP&R': 'EP&R',
     'ASP': 'ASP',
     'Fiscal risk management': 'Fiscal risk\nmanagement',
     'DRF strategies and instruments': 'DRF strategies\nand\ninstruments',
     'Resilient Reconstruction': 'Resilient\nReconstruction'}

    # Replace occurrences based on mapping dictionary d (substring replacements)
for old, new in d.items():
    label_data["individual"] = label_data["individual"].astype(str).str.replace(old, new, regex=False)
for i, row in label_data.iterrows():
    angle = angles[i] + width / 2  # Center of the bar
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
            # print(name, rotation)
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
        
ax.set_frame_on(False)  # Remove the polar plot frame/circle

# Add a red circle at radial value = 1
theta_circle = np.linspace(0, 2 * np.pi, 100)
r_circle = np.ones_like(theta_circle)
ax.plot(theta_circle, r_circle, color='red', linewidth=1, zorder=5, linestyle='--', label="Minimum standard")

# =============================================================================
# 8. FINALIZE PLOT
# =============================================================================

# ax.set_title("DRM System Assessment", y=1.08, fontsize=14, fontweight="bold")
# get existing handles/labels and put "Minimum standard" last
handles, labels = ax.get_legend_handles_labels()
if "Minimum standard" in labels:
    i = labels.index("Minimum standard")
    # remove the minimum standard entry
    h = handles.pop(i)
    l = labels.pop(i)
    # insert it as the second label (index 1). If there's no first label, put at 0.
    insert_pos = 1 if len(labels) >= 1 else 0
    handles.insert(insert_pos, h)
    labels.insert(insert_pos, l)

ax.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, -0.1), ncols=4, fontsize=8, frameon=False)
plt.subplots_adjust(top=0.95, bottom=0.15)

# Save to file
plt.savefig("DRM_Assessment_Chart.png", dpi=300, bbox_inches='tight')
plt.show()
