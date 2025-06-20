"""
# Wheel Drive System

## Theory

A wheel drive system with mass M, rolling resistance B, and traction force F follows the equation:

$$M\dot{v} + Bv = F$$

Where:
- $M$ is the mass (kg)
- $B$ is the rolling resistance coefficient (N·s/m)
- $F$ is the traction force (N)
- $v$ is the velocity (m/s)

This is a first-order linear system. Taking the Laplace transform:

$$MsV(s) + BV(s) = F(s)$$

The transfer function from force to velocity is:

$$G(s) = \frac{V(s)}{F(s)} = \frac{1}{Ms + B}$$

This can be written in standard first-order form:

$$G(s) = \frac{K}{\tau s + 1}$$

Where:
- $K = \frac{1}{B}$ is the DC gain (steady-state velocity per unit force)
- $\tau = \frac{M}{B}$ is the time constant

The system has a single pole at $s = -\frac{B}{M}$ and exhibits exponential behavior with time constant $\tau$.

## Physical Interpretation

- **DC Gain**: $K = 1/B$ represents the steady-state velocity achieved per unit of applied force
- **Time Constant**: $\tau = M/B$ represents how quickly the system responds (63% of final value)
- **Settling Time**: Approximately $4\tau$ (2% criteria) or $3\tau$ (5% criteria)
- **Rolling Resistance**: Higher B means more resistance and slower response
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.optimize import curve_fit
import control as ct

class WheelDrive:
    def __init__(self, M=1000.0, B=100.0):
        """
        Initialize wheel drive parameters
        
        Parameters:
        M (float): Mass (kg)
        B (float): Rolling resistance coefficient (N·s/m)
        """
        self.M = M
        self.B = B
        self.update_system()
    
    def update_system(self):
        """Update the system transfer function and state space representation"""
        # Transfer function: G(s) = 1/(Ms + B)
        num = [1]
        den = [self.M, self.B]
        self.tf = ct.TransferFunction(num, den)
        
        # State space representation: x = v (velocity is the state)
        # v_dot = (-B*v + F)/M
        A = [[-self.B/self.M]]
        B_matrix = [[1/self.M]]
        C = [[1]]  # Output is velocity
        D = [[0]]
        self.ss = ct.StateSpace(A, B_matrix, C, D)
        
        # System characteristics
        self.dc_gain = 1.0 / self.B
        self.time_constant = self.M / self.B
        self.bandwidth = 1.0 / self.time_constant  # -3dB bandwidth
        self.pole = -self.B / self.M
    
    def step_response(self, t_span=None, num_points=1000):
        """
        Generate step response
        
        Parameters:
        t_span (float): Time span for simulation (auto-calculated if None)
        num_points (int): Number of time points
        
        Returns:
        t (array): Time vector
        y (array): Velocity response vector
        """
        if t_span is None:
            t_span = 5 * self.time_constant  # 5 time constants for settling
        
        t = np.linspace(0, t_span, num_points)
        t, y = ct.step_response(self.tf, t)
        return t, y
    
    def impulse_response(self, t_span=None, num_points=1000):
        """Generate impulse response"""
        if t_span is None:
            t_span = 5 * self.time_constant
        
        t = np.linspace(0, t_span, num_points)
        t, y = ct.impulse_response(self.tf, t)
        return t, y
    
    def frequency_response(self, freq_range=None):
        """
        Generate frequency response (Bode plot data)
        
        Parameters:
        freq_range (array): Frequency range in rad/s
        
        Returns:
        freq (array): Frequency vector
        mag (array): Magnitude response
        phase (array): Phase response
        """
        if freq_range is None:
            # Frequency range from 0.1*bandwidth to 100*bandwidth
            f_low = self.bandwidth * 0.01
            f_high = self.bandwidth * 100
            freq_range = np.logspace(np.log10(f_low), np.log10(f_high), 1000)
        
        freq, mag, phase = ct.bode(self.tf, freq_range, plot=False)
        return freq, mag, phase
    
    def simulate(self, force_input, time):
        """
        Simulate system response to arbitrary force input
        
        Parameters:
        force_input (array): Force input vector (N)
        time (array): Time vector (s)
        
        Returns:
        t (array): Time vector
        y (array): Velocity response (m/s)
        """
        t, y = ct.forced_response(self.tf, time, force_input)
        return t, y
    
    def simulate_position(self, force_input, time, initial_position=0):
        """
        Simulate position by integrating velocity
        
        Parameters:
        force_input (array): Force input vector
        time (array): Time vector
        initial_position (float): Initial position
        
        Returns:
        t (array): Time vector
        position (array): Position response
        velocity (array): Velocity response
        """
        t, velocity = self.simulate(force_input, time)
        
        # Integrate velocity to get position
        dt = time[1] - time[0]
        position = np.zeros_like(velocity)
        position[0] = initial_position
        
        for i in range(1, len(position)):
            position[i] = position[i-1] + velocity[i-1] * dt
        
        return t, position, velocity
    
    def steady_state_analysis(self, force_levels):
        """
        Analyze steady-state velocity for different force levels
        
        ## Steady-State Analysis
        
        For a constant force input, the steady-state velocity is:
        $$v_{ss} = \frac{F}{B}$$
        
        Parameters:
        force_levels (array): Different force levels to analyze
        
        Returns:
        velocities (array): Corresponding steady-state velocities
        """
        velocities = force_levels / self.B
        return velocities

def system_identification_wheel(input_data, output_data, time_data):
    """
    Perform system identification to estimate M, B parameters
    
    ## System Identification for First-Order Systems
    
    For a first-order system with step input, the response is:
    $$v(t) = K(1 - e^{-t/\tau})$$
    
    Where $K = F_{step}/B$ is the steady-state gain and $\tau = M/B$ is the time constant.
    
    We can identify:
    1. **DC Gain (K)**: From the final steady-state value
    2. **Time Constant (τ)**: From the time to reach 63% of final value
    3. **Parameters**: $B = F_{step}/K$ and $M = \tau \cdot B$
    
    Parameters:
    input_data (array): Input force data
    output_data (array): Output velocity data
    time_data (array): Time vector
    
    Returns:
    M_est, B_est: Estimated parameters
    """
    
    def first_order_step_response(t, K, tau):
        """First-order step response model"""
        return K * (1 - np.exp(-t/tau))
    
    # Check if input is step-like
    if np.allclose(input_data[10:], input_data[10]):  # Constant input after initial transient
        step_magnitude = input_data[10]
        
        try:
            # Fit first-order model
            popt, pcov = curve_fit(first_order_step_response, time_data, output_data,
                                 bounds=([0, 0.01], [10, 100]),
                                 maxfev=5000)
            K_est, tau_est = popt
            
            # Convert to physical parameters
            # K = 1/B (for unit step) -> B = step_magnitude/K_est
            B_est = step_magnitude / K_est
            M_est = tau_est * B_est
            
            # Calculate parameter uncertainties
            param_std = np.sqrt(np.diag(pcov))
            K_std, tau_std = param_std
            
            print(f"Identification Results:")
            print(f"DC Gain K: {K_est:.4f} ± {K_std:.4f} (m/s)/N")
            print(f"Time Constant τ: {tau_est:.4f} ± {tau_std:.4f} s")
            print(f"Goodness of fit metrics available")
            
        except Exception as e:
            print(f"Curve fitting failed: {e}")
            # Fallback: simple estimation from data
            steady_state = np.mean(output_data[-20:])  # Average of last 20 points
            K_est = steady_state / step_magnitude
            
            # Find time constant (63% of final value)
            target_value = 0.63 * steady_state
            idx_63 = np.argmin(np.abs(output_data - target_value))
            tau_est = time_data[idx_63]
            
            B_est = step_magnitude / K_est
            M_est = tau_est * B_est
    
    else:
        # For non-step inputs, use ARX or other methods
        # Simplified approach: assume reasonable defaults
        print("Non-step input detected. Using simplified identification.")
        
        # Estimate from input-output relationship
        steady_indices = np.where(np.abs(np.diff(output_data)) < 0.001)[0]
        if len(steady_indices) > 10:
            avg_input = np.mean(input_data[steady_indices])
            avg_output = np.mean(output_data[steady_indices])
            B_est = avg_input / avg_output if avg_output != 0 else 100.0
        else:
            B_est = 100.0  # Default
        
        # Estimate time constant from response characteristics
        tau_est = 1.0  # Default
        M_est = tau_est * B_est
    
    return M_est, B_est

def plot_wheel_analysis(wheel, save_plots=False):
    """
    Generate comprehensive plots for wheel drive analysis
    
    Parameters:
    wheel (WheelDrive): System to analyze
    save_plots (bool): Whether to save plots to files
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Wheel Drive Analysis (M={wheel.M}kg, B={wheel.B}N·s/m)', fontsize=14)
    
    # Step response
    t_step, y_step = wheel.step_response()
    axes[0,0].plot(t_step, y_step, 'b-', linewidth=2)
    axes[0,0].axhline(y=wheel.dc_gain, color='r', linestyle='--', alpha=0.7, 
                     label=f'Steady-state: {wheel.dc_gain:.3f} m/s/N')
    axes[0,0].axhline(y=wheel.dc_gain*0.63, color='g', linestyle='--', alpha=0.7,
                     label=f'63% @ t={wheel.time_constant:.2f}s')
    axes[0,0].set_title('Step Response')
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Velocity (m/s)')
    axes[0,0].legend()
    axes[0,0].grid(True)
    
    # Impulse response
    t_imp, y_imp = wheel.impulse_response()
    axes[0,1].plot(t_imp, y_imp, 'b-', linewidth=2)
    axes[0,1].set_title('Impulse Response')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Velocity (m/s)')
    axes[0,1].grid(True)
    
    # Bode plot - Magnitude
    freq, mag, phase = wheel.frequency_response()
    axes[1,0].loglog(freq, np.abs(mag), 'b-', linewidth=2)
    axes[1,0].axvline(x=wheel.bandwidth, color='r', linestyle='--', alpha=0.7,
                     label=f'Bandwidth: {wheel.bandwidth:.3f} rad/s')
    axes[1,0].set_title('Bode Plot - Magnitude')
    axes[1,0].set_xlabel('Frequency (rad/s)')
    axes[1,0].set_ylabel('Magnitude')
    axes[1,0].legend()
    axes[1,0].grid(True)
    
    # Bode plot - Phase
    axes[1,1].semilogx(freq, np.angle(mag)*180/np.pi, 'b-', linewidth=2)
    axes[1,1].axvline(x=wheel.bandwidth, color='r', linestyle='--', alpha=0.7,
                     label=f'Bandwidth: {wheel.bandwidth:.3f} rad/s')
    axes[1,1].set_title('Bode Plot - Phase')
    axes[1,1].set_xlabel('Frequency (rad/s)')
    axes[1,1].set_ylabel('Phase (degrees)')
    axes[1,1].legend()
    axes[1,1].grid(True)
    
    plt.tight_layout()
    
    if save_plots:
        plt.savefig('wheel_drive_analysis.png', dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Print system characteristics
    print(f"System Characteristics:")
    print(f"DC Gain: {wheel.dc_gain:.4f} (m/s)/N")
    print(f"Time Constant: {wheel.time_constant:.3f} s")
    print(f"Bandwidth (-3dB): {wheel.bandwidth:.3f} rad/s")
    print(f"Settling Time (2%): {4*wheel.time_constant:.2f} s")
    print(f"Pole location: {wheel.pole:.3f} rad/s")

def analyze_parameter_effects():
    """
    Analyze the effect of different parameters on system behavior
    
    ## Parameter Sensitivity Analysis
    
    This analysis shows how changes in mass (M) and rolling resistance (B) affect:
    - Time constant: $\tau = M/B$
    - DC gain: $K = 1/B$
    - Bandwidth: $BW = B/M$
    """
    
    print("\n=== Parameter Effects Analysis ===")
    
    # Base parameters
    M_base, B_base = 1000, 100
    
    # Vary mass
    masses = [500, 1000, 2000]
    resistances = [50, 100, 200]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Parameter Effects on Wheel Drive Response', fontsize=14)
    
    # Effect of mass variation
    axes[0,0].set_title('Effect of Mass Variation (B=100 N·s/m)')
    for M in masses:
        wheel = WheelDrive(M=M, B=B_base)
        t, y = wheel.step_response()
        axes[0,0].plot(t, y, label=f'M={M}kg (τ={wheel.time_constant:.2f}s)')
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Velocity (m/s)')
    axes[0,0].legend()
    axes[0,0].grid(True)
    
    # Effect of resistance variation
    axes[0,1].set_title('Effect of Rolling Resistance (M=1000 kg)')
    for B in resistances:
        wheel = WheelDrive(M=M_base, B=B)
        t, y = wheel.step_response()
        axes[0,1].plot(t, y, label=f'B={B}N·s/m (K={wheel.dc_gain:.4f})')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Velocity (m/s)')
    axes[0,1].legend()
    axes[0,1].grid(True)
    
    # Frequency response comparison - mass effect
    axes[1,0].set_title('Frequency Response - Mass Effect')
    for M in masses:
        wheel = WheelDrive(M=M, B=B_base)
        freq, mag, _ = wheel.frequency_response()
        axes[1,0].loglog(freq, np.abs(mag), label=f'M={M}kg')
    axes[1,0].set_xlabel('Frequency (rad/s)')
    axes[1,0].set_ylabel('Magnitude')
    axes[1,0].legend()
    axes[1,0].grid(True)
    
    # Frequency response comparison - resistance effect
    axes[1,1].set_title('Frequency Response - Resistance Effect')
    for B in resistances:
        wheel = WheelDrive(M=M_base, B=B)
        freq, mag, _ = wheel.frequency_response()
        axes[1,1].loglog(freq, np.abs(mag), label=f'B={B}N·s/m')
    axes[1,1].set_xlabel('Frequency (rad/s)')
    axes[1,1].set_ylabel('Magnitude')
    axes[1,1].legend()
    axes[1,1].grid(True)
    
    plt.tight_layout()
    plt.show()

def demonstrate_different_inputs(wheel):
    """
    Demonstrate system response to different input types
    
    ## Input Response Analysis
    
    Shows how the first-order system responds to:
    1. Step input: Exponential approach to steady state
    2. Ramp input: Steady-state error due to no integrator
    3. Sinusoidal input: Frequency-dependent attenuation and phase lag
    """
    
    print(f"\n=== Different Input Responses ===")
    
    t = np.linspace(0, 20, 1000)
    
    # Different input signals
    step_input = np.ones_like(t) * 100  # 100N step
    ramp_input = 10 * t  # 10 N/s ramp
    sine_input = 50 * np.sin(2*np.pi*0.1*t) + 50  # 0.1 Hz sine + DC offset
    
    fig, axes = plt.subplots(3, 2, figsize=(12, 12))
    fig.suptitle('Wheel Drive Response to Different Inputs', fontsize=14)
    
    # Step input
    _, y_step = wheel.simulate(step_input, t)
    axes[0,0].plot(t, step_input, 'r--', label='Input (Force)')
    axes[0,0].set_ylabel('Force (N)')
    axes[0,0].legend()
    axes[0,0].set_title('Step Input')
    axes[0,0].grid(True)
    
    axes[0,1].plot(t, y_step, 'b-', label='Output (Velocity)')
    axes[0,1].axhline(y=step_input[0]/wheel.B, color='g', linestyle=':', 
                     label=f'Steady-state: {step_input[0]/wheel.B:.2f} m/s')
    axes[0,1].set_ylabel('Velocity (m/s)')
    axes[0,1].legend()
    axes[0,1].set_title('Step Response')
    axes[0,1].grid(True)
    
    # Ramp input
    _, y_ramp = wheel.simulate(ramp_input, t)
    axes[1,0].plot(t, ramp_input, 'r--', label='Input (Force)')
    axes[1,0].set_ylabel('Force (N)')
    axes[1,0].legend()
    axes[1,0].set_title('Ramp Input')
    axes[1,0].grid(True)
    
    axes[1,1].plot(t, y_ramp, 'b-', label='Output (Velocity)')
    # Theoretical steady-state response to ramp
    ramp_slope = 10
    steady_state_ramp = ramp_slope * wheel.time_constant  # Steady-state error
    axes[1,1].plot(t, ramp_input/wheel.B - steady_state_ramp, 'g:', 
                  label=f'Ideal - SS error ({steady_state_ramp:.1f} m/s)')
    axes[1,1].set_ylabel('Velocity (m/s)')
    axes[1,1].legend()
    axes[1,1].set_title('Ramp Response')
    axes[1,1].grid(True)
    
    # Sinusoidal input
    _, y_sine = wheel.simulate(sine_input, t)
    axes[2,0].plot(t, sine_input, 'r--', label='Input (Force)')
    axes[2,0].set_ylabel('Force (N)')
    axes[2,0].set_xlabel('Time (s)')
    axes[2,0].legend()
    axes[2,0].set_title('Sinusoidal Input (0.1 Hz)')
    axes[2,0].grid(True)
    
    axes[2,1].plot(t, y_sine, 'b-', label='Output (Velocity)')
    axes[2,1].set_ylabel('Velocity (m/s)')
    axes[2,1].set_xlabel('Time (s)')
    axes[2,1].legend()
    axes[2,1].set_title('Sinusoidal Response')
    axes[2,1].grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Calculate frequency response at the sine frequency
    omega = 2*np.pi*0.1  # 0.1 Hz in rad/s
    magnitude = 1 / np.sqrt((wheel.M*omega)**2 + wheel.B**2)
    phase = -np.arctan(wheel.M*omega/wheel.B) * 180/np.pi
    
    print(f"Sinusoidal Response Analysis (f=0.1 Hz):")
    print(f"Input amplitude: 50 N")
    print(f"Output amplitude: {50*magnitude:.2f} m/s")
    print(f"Phase lag: {-phase:.1f} degrees")
    print(f"Magnitude ratio: {magnitude:.4f}")

def main():
    """
    ## Main Simulation and Analysis
    
    This section demonstrates:
    1. Wheel drive modeling with different parameters
    2. System identification from simulated data
    3. Parameter sensitivity analysis
    4. Response to different input types
    5. Comprehensive analysis and visualization
    """
    
    print("=== Wheel Drive System Analysis ===\n")
    
    # Create wheel drive systems with different characteristics
    
    # Light vehicle (car)
    print("1. Light Vehicle (Car):")
    wheel_car = WheelDrive(M=1500, B=200)  # 1500 kg, moderate resistance
    plot_wheel_analysis(wheel_car)
    
    # Heavy vehicle (truck)
    print("\n2. Heavy Vehicle (Truck):")
    wheel_truck = WheelDrive(M=10000, B=800)  # 10000 kg, high resistance
    plot_wheel_analysis(wheel_truck)
    
    # Light vehicle, low resistance (sports car)
    print("\n3. Sports Car (Low Resistance):")
    wheel_sports = WheelDrive(M=1200, B=100)  # 1200 kg, low resistance
    plot_wheel_analysis(wheel_sports)
    
    # Parameter effects analysis
    analyze_parameter_effects()
    
    # Different input demonstrations
    demonstrate_different_inputs(wheel_car)
    
    # System identification example
    print("\n=== System Identification Example ===")
    
    # Generate synthetic data from known system
    true_wheel = WheelDrive(M=2000, B=150)
    t_data = np.linspace(0, 20, 500)
    force_input = np.ones_like(t_data) * 200  # 200N step input
    _, v_data = true_wheel.simulate(force_input, t_data)
    
    # Add realistic measurement noise
    noise_level = 0.02 * np.max(v_data)  # 2% noise
    v_data_noisy = v_data + noise_level * np.random.randn(len(v_data))
    
    # Perform system identification
    M_est, B_est = system_identification_wheel(force_input, v_data_noisy, t_data)
    
    print(f"\\nTrue parameters: M={true_wheel.M} kg, B={true_wheel.B} N·s/m")
    print(f"Estimated parameters: M={M_est:.1f} kg, B={B_est:.1f} N·s/m")
    print(f"Estimation errors: ΔM={abs(M_est-true_wheel.M)/true_wheel.M*100:.1f}%, "
          f"ΔB={abs(B_est-true_wheel.B)/true_wheel.B*100:.1f}%")
    
    # Compare responses
    estimated_wheel = WheelDrive(M=M_est, B=B_est)
    _, v_est = estimated_wheel.simulate(force_input, t_data)
    
    # Also simulate position for both systems
    _, pos_true, _ = true_wheel.simulate_position(force_input, t_data)
    _, pos_est, _ = estimated_wheel.simulate_position(force_input, t_data)
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Velocity comparison
    axes[0].plot(t_data, v_data, 'b-', label='True System', linewidth=2)
    axes[0].plot(t_data, v_data_noisy, 'r.', label='Noisy Data', alpha=0.6, markersize=2)
    axes[0].plot(t_data, v_est, 'g--', label='Identified System', linewidth=2)
    axes[0].set_ylabel('Velocity (m/s)')
    axes[0].set_title('System Identification Results - Velocity')
    axes[0].legend()
    axes[0].grid(True)
    
    # Position comparison
    axes[1].plot(t_data, pos_true, 'b-', label='True System', linewidth=2)
    axes[1].plot(t_data, pos_est, 'g--', label='Identified System', linewidth=2)
    axes[1].set_ylabel('Position (m)')
    axes[1].set_xlabel('Time (s)')
    axes[1].set_title('System Identification Results - Position')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Performance metrics
    velocity_rmse = np.sqrt(np.mean((v_data - v_est)**2))
    velocity_max_error = np.max(np.abs(v_data - v_est))
    
    print(f"\\nIdentification Performance:")
    print(f"Velocity RMSE: {velocity_rmse:.4f} m/s")
    print(f"Velocity Max Error: {velocity_max_error:.4f} m/s")
    print(f"Final velocity error: {abs(v_data[-1] - v_est[-1]):.4f} m/s")

if __name__ == "__main__":
    main()