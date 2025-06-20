#!/usr/bin/env python3
"""
Generate s-plane visualization for control systems course
Shows stability regions and example pole locations
"""

import matplotlib.pyplot as plt
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

# Set up the s-plane grid
sigma = np.linspace(-6, 2, 100)
omega = np.linspace(-4, 4, 100)

# Create background regions
# Stable region (left half plane)
ax.axvspan(-6, 0, alpha=0.2, color='green', label='Stable Region (LHP)')
# Unstable region (right half plane) 
ax.axvspan(0, 2, alpha=0.2, color='red', label='Unstable Region (RHP)')
# Imaginary axis
ax.axvline(0, color='orange', linewidth=2, alpha=0.7, label='Marginal Stability (jω axis)')

# Plot example poles
# Stable real poles
ax.plot([-4, -2], [0, 0], 'go', markersize=10, label='Stable Real Poles')
ax.annotate('Fast pole\n(s = -4)', (-4, 0), xytext=(-4, -0.8), 
            ha='center', fontsize=9, arrowprops=dict(arrowstyle='->', color='green'))
ax.annotate('Slow pole\n(s = -2)', (-2, 0), xytext=(-2, -0.8), 
            ha='center', fontsize=9, arrowprops=dict(arrowstyle='->', color='green'))

# Stable complex conjugate poles
ax.plot([-1, -1], [2, -2], 'gs', markersize=10, label='Stable Complex Poles')
ax.annotate('Complex poles\n(s = -1 ± j2)', (-1, 2), xytext=(-3, 3), 
            ha='center', fontsize=9, arrowprops=dict(arrowstyle='->', color='green'))

# Unstable poles
ax.plot([1], [0], 'ro', markersize=10, label='Unstable Real Pole')
ax.annotate('Unstable pole\n(s = +1)', (1, 0), xytext=(1, -0.8), 
            ha='center', fontsize=9, arrowprops=dict(arrowstyle='->', color='red'))

# Marginally stable poles
ax.plot([0, 0], [3, -3], 'o', color='orange', markersize=10, label='Marginal Poles')
ax.annotate('Marginal poles\n(s = ±j3)', (0, 3), xytext=(1.5, 3.5), 
            ha='center', fontsize=9, arrowprops=dict(arrowstyle='->', color='orange'))

# Add grid
ax.grid(True, alpha=0.3)

# Set labels and title
ax.set_xlabel('Real Part (σ)', fontsize=12, fontweight='bold')
ax.set_ylabel('Imaginary Part (jω)', fontsize=12, fontweight='bold')
ax.set_title('S-Plane: Pole Locations and Stability Regions', fontsize=14, fontweight='bold')

# Set axis limits
ax.set_xlim(-6, 2)
ax.set_ylim(-4, 4)

# Add text annotations for regions
ax.text(-3, 3.5, 'STABLE\nREGION', fontsize=12, fontweight='bold', 
        ha='center', va='center', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
ax.text(1, 3.5, 'UNSTABLE\nREGION', fontsize=12, fontweight='bold', 
        ha='center', va='center', bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))

# Add legend
ax.legend(loc='lower right', fontsize=10)

# Add key insights as text box
insights_text = """Key Insights:
• Left Half Plane (σ < 0): Stable poles → bounded response
• Right Half Plane (σ > 0): Unstable poles → unbounded response  
• Imaginary Axis (σ = 0): Marginally stable → sustained oscillation
• Distance from origin: Related to response speed
• Complex poles: Create oscillatory behavior"""

ax.text(-5.8, -3.5, insights_text, fontsize=9, 
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
        verticalalignment='bottom')

# Save the figure
plt.tight_layout()
plt.savefig('/home/spensermillburn/sliink/repo/education/control_systems/images/splane_stability.png', 
            dpi=300, bbox_inches='tight')
plt.close()

print("S-plane visualization saved to: /home/spensermillburn/sliink/repo/education/control_systems/images/splane_stability.png")