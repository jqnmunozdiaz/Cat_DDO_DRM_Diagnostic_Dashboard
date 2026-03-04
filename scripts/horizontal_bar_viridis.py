#%%
"""
Horizontal bar chart with Viridis colormap.
Creates a horizontal bar chart demonstrating the Viridis color gradient.
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Define Viridis color map
VIRIDIS_COLORS = [
    (0.0, '#440154'), (0.25, '#3b528b'), (0.5, '#21918c'), 
    (0.75, '#5ec962'), (1.0, '#fde725')
]

# Create custom colormap from the defined colors
cmap = mcolors.LinearSegmentedColormap.from_list(
    'viridis_custom', 
    [color for _, color in VIRIDIS_COLORS]
)

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 2))

# Total bar width
total_value = 100
n_segments = 500  # Number of segments for smooth gradient

# Create gradient bar by plotting multiple thin segments
y_position = 0
bar_height = 0.6

for i in range(n_segments):
    # Calculate color for this segment
    color_position = i / (n_segments - 1)
    color = cmap(color_position)
    
    # Create a thin segment
    segment_width = total_value / n_segments
    ax.barh(y_position, segment_width, left=i * segment_width, 
            height=bar_height, color=color, edgecolor='none')

# Customize the plot

# Remove y-axis labels and ticks
ax.set_yticks([])
ax.set_yticklabels([])

# Remove spines (box around plot)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)

# Add custom vertical grid lines from bottom to bar
for tick_pos in [0, 25, 50, 75, 100]:
    ax.plot([tick_pos, tick_pos], [-0.5, -bar_height/2], 
            color='gray', alpha=0.3, linestyle='--', linewidth=1)

# Set x-axis limits
ax.set_xlim(0, total_value)
ax.set_ylim(-0.5, 0.5)

# Set custom x-axis ticks at 0, 25%, 50%, 75%, 100%
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'], fontsize=13, fontweight='bold')

# Add maturity level labels below the bar
maturity_labels = [
    ('Nascent', 12.5),      # Between 0% and 25%
    ('Emerging', 37.5),     # Between 25% and 50%
    ('Established', 62.5),  # Between 50% and 75%
    ('Mature', 87.5)        # Between 75% and 100%
]

for label, position in maturity_labels:
    ax.text(position, y_position - 0.5, label, 
            ha='center', va='top', 
            fontsize=14, fontweight='bold', 
            color='black')

# Adjust layout to prevent label cutoff with minimal padding
plt.tight_layout(pad=0.2)

# Save the figure
output_path = 'G:/My Drive/World_Bank_DRM/Cat_DDO_DRM_Diagnostic_Dashboard/assets/images/horizontal_bar_viridis.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to: {output_path}")

# Display the plot
plt.show()

# %%
