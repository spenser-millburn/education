#!/usr/bin/env python3
"""
Generate all visualization plots for control systems course overview
Creates one key plot per major section
"""

import matplotlib.pyplot as plt
import numpy as np
import control as ct
from scipy import signal
import os

# Create images directory if it doesn't exist
os.makedirs('/home/spensermillburn/sliink/repo/education/control_systems/images', exist_ok=True)

# Set matplotlib parameters for consistent styling
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# 1. BLOCK DIAGRAM REDUCTION EXAMPLE
def create_block_diagram_reduction():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Complex system (before reduction)
    ax1.text(0.5, 0.8, 'BEFORE REDUCTION: Complex Multi-Loop System', 
             ha='center', va='center', fontsize=14, fontweight='bold', transform=ax1.transAxes)
    
    # Draw complex block diagram using text and arrows
    ax1.text(0.1, 0.5, 'R(s)', ha='center', va='center', fontsize=12, 
             bbox=dict(boxstyle='round', facecolor='lightblue'))
    ax1.text(0.25, 0.5, 'G₁', ha='center', va='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax1.text(0.4, 0.5, 'G₂', ha='center', va='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax1.text(0.55, 0.5, 'G₃', ha='center', va='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax1.text(0.7, 0.5, 'C(s)', ha='center', va='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightcoral'))
    
    # Feedback paths
    ax1.text(0.4, 0.2, 'H₁', ha='center', va='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightyellow'))
    ax1.text(0.55, 0.2, 'H₂', ha='center', va='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightyellow'))
    
    # Add arrows
    ax1.annotate('', xy=(0.2, 0.5), xytext=(0.15, 0.5), 
                arrowprops=dict(arrowstyle='->', lw=2))
    ax1.annotate('', xy=(0.35, 0.5), xytext=(0.3, 0.5), 
                arrowprops=dict(arrowstyle='->', lw=2))
    ax1.annotate('', xy=(0.5, 0.5), xytext=(0.45, 0.5), 
                arrowprops=dict(arrowstyle='->', lw=2))
    ax1.annotate('', xy=(0.65, 0.5), xytext=(0.6, 0.5), 
                arrowprops=dict(arrowstyle='->', lw=2))
    
    ax1.text(0.5, 0.1, 'Multiple feedback loops make analysis complex', 
             ha='center', va='center', fontsize=11, style='italic')
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    
    # Simple system (after reduction)
    ax2.text(0.5, 0.8, 'AFTER REDUCTION: Single Equivalent Block', 
             ha='center', va='center', fontsize=14, fontweight='bold', transform=ax2.transAxes)
    
    ax2.text(0.2, 0.5, 'R(s)', ha='center', va='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightblue'))
    ax2.text(0.5, 0.5, 'G₁G₂G₃/(1+G₁G₂H₁+G₂G₃H₂)', ha='center', va='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax2.text(0.8, 0.5, 'C(s)', ha='center', va='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightcoral'))
    
    # Arrows
    ax2.annotate('', xy=(0.35, 0.5), xytext=(0.25, 0.5), 
                arrowprops=dict(arrowstyle='->', lw=2))
    ax2.annotate('', xy=(0.75, 0.5), xytext=(0.65, 0.5), 
                arrowprops=dict(arrowstyle='->', lw=2))
    
    ax2.text(0.5, 0.2, 'Single transfer function - easy to analyze!', 
             ha='center', va='center', fontsize=11, style='italic', color='green')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/spensermillburn/sliink/repo/education/control_systems/images/block_diagram_reduction.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

# 2. TIME RESPONSE ANALYSIS - Second Order System Variations
def create_time_response_analysis():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Time vector
    t = np.linspace(0, 8, 1000)
    
    # Different damping ratios
    damping_ratios = [0.1, 0.5, 0.707, 1.0, 2.0]
    colors = ['red', 'orange', 'green', 'blue', 'purple']
    labels = ['Underdamped (ζ=0.1)', 'Underdamped (ζ=0.5)', 'Critically Damped (ζ=0.707)', 
              'Critically Damped (ζ=1.0)', 'Overdamped (ζ=2.0)']
    
    wn = 2  # Natural frequency
    
    for i, zeta in enumerate(damping_ratios):
        # Create second-order system
        num = [wn**2]
        den = [1, 2*zeta*wn, wn**2]
        system = ct.TransferFunction(num, den)
        
        # Step response
        t_out, y_out = ct.step_response(system, t)
        
        ax.plot(t_out, y_out, color=colors[i], linewidth=2, label=labels[i])
    
    # Add reference line
    ax.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Steady-state value')
    
    # Annotations for key metrics
    ax.annotate('Overshoot', xy=(1.5, 1.65), xytext=(3, 1.8),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, color='red')
    ax.annotate('Rise Time', xy=(0.8, 0.9), xytext=(2, 0.5),
                arrowprops=dict(arrowstyle='->', color='blue'),
                fontsize=10, color='blue')
    ax.annotate('Settling Time', xy=(4, 1.02), xytext=(5.5, 1.5),
                arrowprops=dict(arrowstyle='->', color='green'),
                fontsize=10, color='green')
    
    ax.set_xlabel('Time (seconds)', fontweight='bold')
    ax.set_ylabel('Amplitude', fontweight='bold')
    ax.set_title('Second-Order System Step Response: Effect of Damping Ratio', fontweight='bold')
    ax.legend(loc='right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 2)
    
    plt.tight_layout()
    plt.savefig('/home/spensermillburn/sliink/repo/education/control_systems/images/time_response_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

# 3. FREQUENCY RESPONSE ANALYSIS - Bode Plot
def create_frequency_response_analysis():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Create a second-order system
    wn = 10  # rad/s
    zeta = 0.3
    num = [wn**2]
    den = [1, 2*zeta*wn, wn**2]
    system = ct.TransferFunction(num, den)
    
    # Frequency range
    w = np.logspace(-1, 2, 1000)
    
    # Get frequency response
    mag, phase, omega = ct.frequency_response(system, w)
    
    # Convert to dB
    mag_db = 20 * np.log10(np.abs(mag))
    phase_deg = np.angle(mag) * 180 / np.pi
    
    # Magnitude plot
    ax1.semilogx(omega, mag_db, 'b-', linewidth=2)
    ax1.set_ylabel('Magnitude (dB)', fontweight='bold')
    ax1.set_title('Bode Plot: Second-Order System (ωₙ=10 rad/s, ζ=0.3)', fontweight='bold')
    ax1.grid(True, which="both", alpha=0.3)
    
    # Mark important frequencies
    resonant_freq = wn * np.sqrt(1 - 2*zeta**2)
    ax1.axvline(resonant_freq, color='red', linestyle='--', alpha=0.7, label=f'Resonant freq = {resonant_freq:.1f} rad/s')
    ax1.axvline(wn, color='green', linestyle='--', alpha=0.7, label=f'Natural freq = {wn} rad/s')
    ax1.axhline(-3, color='orange', linestyle='--', alpha=0.7, label='-3dB line')
    ax1.legend()
    
    # Phase plot
    ax2.semilogx(omega, phase_deg, 'r-', linewidth=2)
    ax2.set_ylabel('Phase (degrees)', fontweight='bold')
    ax2.set_xlabel('Frequency (rad/s)', fontweight='bold')
    ax2.grid(True, which="both", alpha=0.3)
    ax2.axvline(wn, color='green', linestyle='--', alpha=0.7)
    ax2.axhline(-90, color='orange', linestyle='--', alpha=0.7, label='-90° line')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('/home/spensermillburn/sliink/repo/education/control_systems/images/frequency_response_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

# 4. ROOT LOCUS ANALYSIS
def create_root_locus_analysis():
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Define open-loop system G(s) = K / (s(s+2)(s+5))
    num = [1]
    den = [1, 7, 10, 0]  # s^3 + 7s^2 + 10s = s(s+2)(s+5)
    system = ct.TransferFunction(num, den)
    
    # Create root locus
    rlist, klist = ct.root_locus(system, plot=False)
    
    # Plot root locus
    for i in range(len(rlist[0])):
        ax.plot(rlist[:, i].real, rlist[:, i].imag, 'b-', linewidth=2, alpha=0.7)
    
    # Mark poles and zeros
    poles = np.roots(den)
    ax.plot(poles.real, poles.imag, 'rx', markersize=10, markeredgewidth=3, label='Open-loop Poles')
    
    # Add stability boundary
    ax.axvline(0, color='red', linestyle='--', alpha=0.5, linewidth=2, label='Stability Boundary')
    
    # Shade stable region
    ax.axvspan(-8, 0, alpha=0.1, color='green', label='Stable Region')
    ax.axvspan(0, 2, alpha=0.1, color='red', label='Unstable Region')
    
    # Mark some specific K values
    K_values = [0, 10, 30, 60]
    for K in K_values:
        if K == 0:
            continue
        # Find closed-loop poles for this K
        cl_system = ct.feedback(K * system, 1)
        cl_poles = ct.poles(cl_system)
        ax.plot(cl_poles.real, cl_poles.imag, 'go', markersize=8, alpha=0.8)
        
        # Add K value annotation
        for pole in cl_poles:
            if pole.imag >= 0:  # Only annotate upper half
                ax.annotate(f'K={K}', (pole.real, pole.imag), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax.set_xlabel('Real Part', fontweight='bold')
    ax.set_ylabel('Imaginary Part', fontweight='bold')
    ax.set_title('Root Locus: G(s) = K/[s(s+2)(s+5)]', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_xlim(-8, 2)
    ax.set_ylim(-6, 6)
    
    # Add annotations
    ax.text(-4, 5, 'Poles move with\nincreasing gain K', fontsize=10, 
            bbox=dict(boxstyle='round', facecolor='lightyellow'))
    
    plt.tight_layout()
    plt.savefig('/home/spensermillburn/sliink/repo/education/control_systems/images/root_locus_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

# 5. PID CONTROLLER COMPARISON
def create_pid_controller_comparison():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plant: second-order system
    wn = 2
    zeta = 0.1
    plant_num = [wn**2]
    plant_den = [1, 2*zeta*wn, wn**2]
    plant = ct.TransferFunction(plant_num, plant_den)
    
    # Time vector
    t = np.linspace(0, 10, 1000)
    
    # Different controllers
    controllers = {
        'P (Kp=5)': ct.TransferFunction([5], [1]),
        'PI (Kp=5, Ki=2)': ct.TransferFunction([5, 2], [1, 0]),
        'PD (Kp=5, Kd=1)': ct.TransferFunction([1, 5], [1]),
        'PID (Kp=5, Ki=2, Kd=1)': ct.TransferFunction([1, 5, 2], [1, 0])
    }
    
    colors = ['red', 'blue', 'green', 'purple']
    
    for i, (name, controller) in enumerate(controllers.items()):
        # Closed-loop system
        cl_system = ct.feedback(controller * plant, 1)
        
        # Step response
        t_out, y_out = ct.step_response(cl_system, t)
        
        ax.plot(t_out, y_out, color=colors[i], linewidth=2, label=name)
    
    # Reference line
    ax.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Reference')
    
    ax.set_xlabel('Time (seconds)', fontweight='bold')
    ax.set_ylabel('Output', fontweight='bold')
    ax.set_title('PID Controller Comparison: Step Response', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.5)
    
    # Add performance annotations
    ax.text(7, 1.3, 'Key Observations:\n• P: Fast but steady-state error\n• PI: Zero error, some overshoot\n• PD: Good damping, has error\n• PID: Best overall performance', 
            fontsize=9, bbox=dict(boxstyle='round', facecolor='lightyellow'))
    
    plt.tight_layout()
    plt.savefig('/home/spensermillburn/sliink/repo/education/control_systems/images/pid_controller_comparison.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

# 6. NYQUIST PLOT ANALYSIS
def create_nyquist_plot_analysis():
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create a system that's marginally stable
    # G(s) = K / (s(s+1)(s+2))
    K = 6  # Choose K for interesting behavior
    num = [K]
    den = [1, 3, 2, 0]  # s^3 + 3s^2 + 2s = s(s+1)(s+2)
    system = ct.TransferFunction(num, den)
    
    # Frequency range
    w = np.logspace(-2, 2, 1000)
    
    # Get frequency response
    _, _, omega = ct.frequency_response(system, w)
    real_part = []
    imag_part = []
    
    for freq in omega:
        response = system(1j * freq)
        real_part.append(response.real)
        imag_part.append(response.imag)
    
    real_part = np.array(real_part)
    imag_part = np.array(imag_part)
    
    # Plot Nyquist diagram
    ax.plot(real_part, imag_part, 'b-', linewidth=2, label='G(jω)')
    ax.plot(real_part, -imag_part, 'b--', linewidth=2, alpha=0.7, label='G(-jω)')
    
    # Mark critical point (-1, 0)
    ax.plot(-1, 0, 'ro', markersize=12, markeredgewidth=2, label='Critical Point (-1,0)')
    ax.annotate('(-1, 0)', (-1, 0), xytext=(-1.3, 0.2), fontsize=12, fontweight='bold')
    
    # Mark some frequency points
    freq_points = [0.1, 1, 10]
    for fp in freq_points:
        if fp in omega:
            idx = np.argmin(np.abs(omega - fp))
            ax.plot(real_part[idx], imag_part[idx], 'go', markersize=8)
            ax.annotate(f'ω={fp}', (real_part[idx], imag_part[idx]), 
                       xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    # Add unit circle for reference
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(theta), np.sin(theta), 'k:', alpha=0.3, label='Unit Circle')
    
    ax.set_xlabel('Real Part', fontweight='bold')
    ax.set_ylabel('Imaginary Part', fontweight='bold')
    ax.set_title('Nyquist Plot: G(s) = 6/[s(s+1)(s+2)]', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axis('equal')
    ax.set_xlim(-3, 1)
    ax.set_ylim(-2, 2)
    
    # Add stability annotation
    ax.text(0.5, 1.5, 'Stability Analysis:\nNo encirclement of (-1,0)\n→ System is stable', 
            fontsize=10, bbox=dict(boxstyle='round', facecolor='lightgreen'))
    
    plt.tight_layout()
    plt.savefig('/home/spensermillburn/sliink/repo/education/control_systems/images/nyquist_plot_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

# 7. CONTROL SYSTEM PERFORMANCE TRADE-OFFS
def create_performance_tradeoffs():
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create a 2D visualization of the trade-off space
    # Speed vs Stability trade-off
    speed = np.linspace(0, 10, 100)
    stability_1 = 10 / (1 + speed/2)  # Inverse relationship
    stability_2 = 8 / (1 + speed/3)   # Different curve
    stability_3 = 6 / (1 + speed/4)   # Another curve
    
    ax.plot(speed, stability_1, 'r-', linewidth=3, label='Low Accuracy Requirement')
    ax.plot(speed, stability_2, 'b-', linewidth=3, label='Medium Accuracy Requirement')
    ax.plot(speed, stability_3, 'g-', linewidth=3, label='High Accuracy Requirement')
    
    # Fill areas to show trade-off regions
    ax.fill_between(speed, 0, stability_3, alpha=0.2, color='red', label='Unachievable Region')
    ax.fill_between(speed, stability_3, stability_1, alpha=0.2, color='yellow', label='Challenging Region')
    ax.fill_between(speed, stability_1, 10, alpha=0.2, color='green', label='Achievable Region')
    
    # Mark some design points
    design_points = [
        (2, 7, 'Conservative Design'),
        (5, 4, 'Balanced Design'),
        (8, 2, 'Aggressive Design')
    ]
    
    for x, y, label in design_points:
        ax.plot(x, y, 'ko', markersize=10)
        ax.annotate(label, (x, y), xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.set_xlabel('Response Speed (Higher = Faster)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Stability Margin (Higher = More Stable)', fontweight='bold', fontsize=12)
    ax.set_title('Control System Design Trade-offs: Speed vs Stability vs Accuracy', 
                fontweight='bold', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    
    # Add explanatory text
    ax.text(1, 9, 'The Fundamental Trade-off:\n• Faster response → Less stable\n• Higher accuracy → More complex\n• Better performance → Higher cost', 
            fontsize=11, bbox=dict(boxstyle='round', facecolor='lightyellow'))
    
    plt.tight_layout()
    plt.savefig('/home/spensermillburn/sliink/repo/education/control_systems/images/performance_tradeoffs.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

# Main execution
if __name__ == "__main__":
    print("Generating control systems visualizations...")
    
    try:
        create_block_diagram_reduction()
        print("✓ Block diagram reduction plot created")
        
        create_time_response_analysis()
        print("✓ Time response analysis plot created")
        
        create_frequency_response_analysis()
        print("✓ Frequency response analysis plot created")
        
        create_root_locus_analysis()
        print("✓ Root locus analysis plot created")
        
        create_pid_controller_comparison()
        print("✓ PID controller comparison plot created")
        
        create_nyquist_plot_analysis()
        print("✓ Nyquist plot analysis created")
        
        create_performance_tradeoffs()
        print("✓ Performance trade-offs plot created")
        
        print("\nAll visualizations completed successfully!")
        print("Images saved to: /home/spensermillburn/sliink/repo/education/control_systems/images/")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure 'control' library is installed: pip install control")