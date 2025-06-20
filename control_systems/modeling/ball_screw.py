"""
# Ball Screw System

## Theory

A ball screw system with mass M, damping B, and axial force F follows the equation:

$$M\ddot{x} + B\dot{x} = F$$

Where:
- $M$ is the mass (kg)
- $B$ is the damping coefficient (N·s/m)
- $F$ is the axial force (N)
- $x$ is the position (m)

This is a second-order system with double integrator behavior. Taking the Laplace transform:

$$Ms^2X(s) + BsX(s) = F(s)$$

The transfer function from force to position is:

$$G(s) = \frac{X(s)}{F(s)} = \frac{1}{Ms^2 + Bs} = \frac{1}{s(Ms + B)}$$

This can be rewritten as:

$$G(s) = \frac{1/B}{s(\tau s + 1)}$$

Where $\tau = \frac{M}{B}$ is the time constant.

For velocity output, the transfer function becomes:

$$G_v(s) = \frac{sX(s)}{F(s)} = \frac{1}{Ms + B}$$

This is a first-order system identical to the wheel drive case.

## Key Characteristics

- **Double Integrator**: The system has poles at $s = 0$ and $s = -B/M$
- **Marginally Stable**: The integrator at the origin makes the system marginally stable
- **No Spring**: Unlike the linear actuator, there's no restoring force
- **Velocity Response**: First-order with time constant $\tau = M/B$
- **Position Response**: Ramp response to step input with steady-state velocity $F/B$

## Applications

Ball screws are commonly used in:
- CNC machine tool axes
- 3D printers (Z-axis)
- Linear actuators
- Precision positioning systems
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.optimize import curve_fit
import control as ct

class BallScrew:
    def __init__(self, M=10.0, B=50.0):
        """
        Initialize ball screw parameters
        
        Parameters:
        M (float): Mass (kg)
        B (float): Damping coefficient (N·s/m)
        """
        self.M = M
        self.B = B
        self.update_system()
    
    def update_system(self):
        """Update the system transfer function and state space representation"""
        # Transfer function from force to position: G(s) = 1/(s(Ms + B))
        num_pos = [1]
        den_pos = [self.M, self.B, 0]
        self.tf_position = ct.TransferFunction(num_pos, den_pos)
        
        # Transfer function from force to velocity: G(s) = 1/(Ms + B)
        num_vel = [1]
        den_vel = [self.M, self.B]
        self.tf_velocity = ct.TransferFunction(num_vel, den_vel)
        
        # State space representation: x1 = x (position), x2 = x_dot (velocity)
        # x_dot = x2, x_ddot = (-B*x2 + F)/M
        A = [[0, 1], [0, -self.B/self.M]]
        B_matrix = [[0], [1/self.M]]
        C_pos = [[1, 0]]  # Position output
        C_vel = [[0, 1]]  # Velocity output
        D_matrix = [[0]]
        
        self.ss_position = ct.StateSpace(A, B_matrix, C_pos, D_matrix)
        self.ss_velocity = ct.StateSpace(A, B_matrix, C_vel, D_matrix)
        
        # System characteristics
        self.time_constant = self.M / self.B
        self.dc_gain_velocity = 1.0 / self.B  # Steady-state velocity per unit force
        self.pole_velocity = -self.B / self.M
        self.poles_position = [0, -self.B/self.M]  # Integrator + first-order
    
    def step_response_position(self, t_span=None, num_points=1000):
        """
        Generate step response for position
        
        For a step input, position shows ramp behavior approaching steady-state velocity.
        
        Parameters:
        t_span (float): Time span for simulation
        num_points (int): Number of time points
        
        Returns:
        t (array): Time vector
        y (array): Position response vector
        """
        if t_span is None:
            t_span = 10 * self.time_constant  # Longer time to see steady-state behavior
        
        t = np.linspace(0, t_span, num_points)
        t, y = ct.step_response(self.tf_position, t)
        return t, y
    
    def step_response_velocity(self, t_span=None, num_points=1000):
        """Generate step response for velocity"""
        if t_span is None:
            t_span = 5 * self.time_constant
        
        t = np.linspace(0, t_span, num_points)
        t, y = ct.step_response(self.tf_velocity, t)
        return t, y
    
    def impulse_response_position(self, t_span=None, num_points=1000):
        """Generate impulse response for position"""
        if t_span is None:
            t_span = 5 * self.time_constant
        
        t = np.linspace(0, t_span, num_points)
        t, y = ct.impulse_response(self.tf_position, t)
        return t, y
    
    def impulse_response_velocity(self, t_span=None, num_points=1000):
        """Generate impulse response for velocity"""
        if t_span is None:
            t_span = 5 * self.time_constant
        
        t = np.linspace(0, t_span, num_points)
        t, y = ct.impulse_response(self.tf_velocity, t)
        return t, y
    
    def frequency_response_position(self, freq_range=None):
        """
        Generate frequency response for position (Bode plot data)
        
        The position response has:
        - 20 dB/decade roll-off from integrator at low frequencies
        - Additional 20 dB/decade roll-off above corner frequency (B/M)
        - Total 40 dB/decade roll-off at high frequencies
        
        Parameters:
        freq_range (array): Frequency range in rad/s
        
        Returns:
        freq (array): Frequency vector
        mag (array): Magnitude response
        phase (array): Phase response
        """
        if freq_range is None:
            corner_freq = self.B / self.M
            f_low = corner_freq * 0.01
            f_high = corner_freq * 100
            freq_range = np.logspace(np.log10(f_low), np.log10(f_high), 1000)
        
        freq, mag, phase = ct.bode(self.tf_position, freq_range, plot=False)
        return freq, mag, phase
    
    def frequency_response_velocity(self, freq_range=None):
        """Generate frequency response for velocity"""
        if freq_range is None:
            corner_freq = self.B / self.M
            f_low = corner_freq * 0.01
            f_high = corner_freq * 100
            freq_range = np.logspace(np.log10(f_low), np.log10(f_high), 1000)
        
        freq, mag, phase = ct.bode(self.tf_velocity, freq_range, plot=False)
        return freq, mag, phase
    
    def simulate_position(self, force_input, time):
        """
        Simulate position response to arbitrary force input
        
        Parameters:
        force_input (array): Force input vector
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        y (array): Position response
        """
        t, y = ct.forced_response(self.tf_position, time, force_input)
        return t, y
    
    def simulate_velocity(self, force_input, time):
        """Simulate velocity response to arbitrary force input"""
        t, y = ct.forced_response(self.tf_velocity, time, force_input)
        return t, y
    
    def simulate_full_state(self, force_input, time):
        """
        Simulate both position and velocity simultaneously
        
        Parameters:
        force_input (array): Force input vector
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        position (array): Position response
        velocity (array): Velocity response
        """
        # Use state space model to get both outputs
        ss_both = ct.StateSpace(self.ss_position.A, self.ss_position.B, 
                               [[1, 0], [0, 1]], [[0], [0]])
        
        t, y = ct.forced_response(ss_both, time, force_input)
        position = y[0]
        velocity = y[1]
        
        return t, position, velocity
    
    def analyze_tracking_performance(self, reference_trajectory, time):
        """
        Analyze system's ability to track a reference trajectory
        
        ## Tracking Analysis
        
        For position tracking, we need to determine the required force input
        to achieve a desired position trajectory. This involves:
        
        $$F_{required} = M\ddot{x}_{ref} + B\dot{x}_{ref}$$
        
        Parameters:
        reference_trajectory (array): Desired position trajectory
        time (array): Time vector
        
        Returns:
        required_force (array): Force needed for perfect tracking
        tracking_error (array): Error when using feedforward control
        """
        dt = time[1] - time[0]
        
        # Calculate derivatives of reference trajectory
        velocity_ref = np.gradient(reference_trajectory, dt)
        acceleration_ref = np.gradient(velocity_ref, dt)
        
        # Required force for perfect tracking (feedforward)
        required_force = self.M * acceleration_ref + self.B * velocity_ref
        
        # Simulate actual response with this force
        t_sim, actual_position = self.simulate_position(required_force, time)
        tracking_error = reference_trajectory - actual_position
        
        return required_force, tracking_error, velocity_ref, acceleration_ref

def system_identification_ballscrew(input_data, output_data, time_data, output_type='velocity'):
    """
    Perform system identification to estimate M, B parameters
    
    ## System Identification for Ball Screw
    
    For velocity output (first-order system):
    $$G_v(s) = \frac{1}{Ms + B} = \frac{K}{\tau s + 1}$$
    
    Where $K = 1/B$ and $\tau = M/B$.
    
    For position output (integrator + first-order):
    $$G_p(s) = \frac{1}{s(Ms + B)}$$
    
    The step response is: $x(t) = \frac{F}{B}(t - \tau(1 - e^{-t/\tau}))$
    
    Parameters:
    input_data (array): Input force data
    output_data (array): Output data (position or velocity)
    time_data (array): Time vector
    output_type (str): 'velocity' or 'position'
    
    Returns:
    M_est, B_est: Estimated parameters
    """
    
    if output_type == 'velocity':
        # First-order system identification (same as wheel drive)
        def first_order_step(t, K, tau):
            """First-order step response: K*(1 - exp(-t/tau))"""
            return K * (1 - np.exp(-t/tau))
        
        if np.allclose(input_data[10:], input_data[10]):  # Step input
            try:
                step_magnitude = input_data[10]
                normalized_output = output_data / step_magnitude
                
                popt, pcov = curve_fit(first_order_step, time_data, normalized_output,
                                     bounds=([0, 0.01], [1, 100]),
                                     maxfev=5000)
                K_est, tau_est = popt
                
                # Convert to physical parameters
                B_est = step_magnitude / K_est
                M_est = tau_est * B_est
                
                # Calculate uncertainties
                param_std = np.sqrt(np.diag(pcov))
                print(f"Velocity ID - K: {K_est:.4f} ± {param_std[0]:.4f} (m/s)/N")
                print(f"Velocity ID - τ: {tau_est:.4f} ± {param_std[1]:.4f} s")
                
            except Exception as e:
                print(f"Velocity curve fitting failed: {e}")
                # Fallback estimation
                steady_state = np.mean(output_data[-20:])
                K_est = steady_state / input_data[10]
                tau_est = 1.0  # Default
                B_est = input_data[10] / K_est
                M_est = tau_est * B_est
        else:
            # Non-step input - simplified approach
            M_est, B_est = 10.0, 50.0  # Default values
    
    else:  # position output
        # Integrator + first-order system
        def integrator_first_order_step(t, K, tau):
            """Step response of integrator + first-order: K*(t - tau*(1 - exp(-t/tau)))"""
            return K * (t - tau * (1 - np.exp(-t/tau)))
        
        if np.allclose(input_data[10:], input_data[10]):  # Step input
            try:
                step_magnitude = input_data[10]
                normalized_output = output_data / step_magnitude
                
                # Initial guess based on data
                final_slope = np.mean(np.diff(output_data[-50:]) / np.diff(time_data[-50:]))
                K_guess = final_slope / step_magnitude
                
                popt, pcov = curve_fit(integrator_first_order_step, time_data, normalized_output,
                                     p0=[K_guess, 1.0],
                                     bounds=([0, 0.01], [1, 100]),
                                     maxfev=5000)
                K_est, tau_est = popt
                
                # Convert to physical parameters
                # K = 1/B for the steady-state slope
                B_est = step_magnitude / K_est
                M_est = tau_est * B_est
                
                param_std = np.sqrt(np.diag(pcov))
                print(f"Position ID - K: {K_est:.4f} ± {param_std[0]:.4f} m/s/N")
                print(f"Position ID - τ: {tau_est:.4f} ± {param_std[1]:.4f} s")
                
            except Exception as e:
                print(f"Position curve fitting failed: {e}")
                # Estimate from steady-state slope
                final_slope = np.mean(np.diff(output_data[-50:]) / np.diff(time_data[-50:]))
                B_est = input_data[10] / final_slope if final_slope > 0 else 50.0
                M_est = 1.0 * B_est  # Assume tau = 1
        else:
            M_est, B_est = 10.0, 50.0
    
    return M_est, B_est

def plot_ballscrew_analysis(ballscrew, save_plots=False):
    """
    Generate comprehensive plots for ball screw analysis
    
    Parameters:
    ballscrew (BallScrew): System to analyze
    save_plots (bool): Whether to save plots to files
    """
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle(f'Ball Screw Analysis (M={ballscrew.M}kg, B={ballscrew.B}N·s/m)', 
                 fontsize=14)
    
    # Position step response
    t_pos, y_pos = ballscrew.step_response_position()
    axes[0,0].plot(t_pos, y_pos, 'b-', linewidth=2)
    # Show steady-state slope
    steady_slope = ballscrew.dc_gain_velocity
    t_end = t_pos[-1]
    y_steady = steady_slope * t_pos  # Linear growth
    axes[0,0].plot(t_pos, y_steady, 'r--', alpha=0.7, 
                  label=f'Steady slope: {steady_slope:.4f} m/s')
    axes[0,0].set_title('Position Step Response')
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Position (m)')
    axes[0,0].legend()
    axes[0,0].grid(True)
    
    # Velocity step response
    t_vel, y_vel = ballscrew.step_response_velocity()
    axes[0,1].plot(t_vel, y_vel, 'b-', linewidth=2)
    axes[0,1].axhline(y=ballscrew.dc_gain_velocity, color='r', linestyle='--', alpha=0.7,
                     label=f'Steady-state: {ballscrew.dc_gain_velocity:.4f} m/s')
    axes[0,1].axhline(y=ballscrew.dc_gain_velocity*0.63, color='g', linestyle='--', alpha=0.7,
                     label=f'63% @ t={ballscrew.time_constant:.2f}s')
    axes[0,1].set_title('Velocity Step Response')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Velocity (m/s)')
    axes[0,1].legend()
    axes[0,1].grid(True)
    
    # Position frequency response - Magnitude
    freq_pos, mag_pos, phase_pos = ballscrew.frequency_response_position()
    axes[1,0].loglog(freq_pos, np.abs(mag_pos), 'b-', linewidth=2)
    corner_freq = ballscrew.B / ballscrew.M
    axes[1,0].axvline(x=corner_freq, color='r', linestyle='--', alpha=0.7,
                     label=f'Corner freq: {corner_freq:.3f} rad/s')
    axes[1,0].set_title('Position Bode - Magnitude')
    axes[1,0].set_xlabel('Frequency (rad/s)')
    axes[1,0].set_ylabel('Magnitude')
    axes[1,0].legend()
    axes[1,0].grid(True)
    
    # Velocity frequency response - Magnitude
    freq_vel, mag_vel, phase_vel = ballscrew.frequency_response_velocity()
    axes[1,1].loglog(freq_vel, np.abs(mag_vel), 'b-', linewidth=2)
    axes[1,1].axvline(x=corner_freq, color='r', linestyle='--', alpha=0.7,
                     label=f'Corner freq: {corner_freq:.3f} rad/s')
    axes[1,1].set_title('Velocity Bode - Magnitude')
    axes[1,1].set_xlabel('Frequency (rad/s)')
    axes[1,1].set_ylabel('Magnitude')
    axes[1,1].legend()
    axes[1,1].grid(True)
    
    # Phase plots
    axes[2,0].semilogx(freq_pos, np.angle(mag_pos)*180/np.pi, 'b-', linewidth=2)
    axes[2,0].axvline(x=corner_freq, color='r', linestyle='--', alpha=0.7)
    axes[2,0].set_title('Position Bode - Phase')
    axes[2,0].set_xlabel('Frequency (rad/s)')
    axes[2,0].set_ylabel('Phase (degrees)')
    axes[2,0].grid(True)
    
    axes[2,1].semilogx(freq_vel, np.angle(mag_vel)*180/np.pi, 'b-', linewidth=2)
    axes[2,1].axvline(x=corner_freq, color='r', linestyle='--', alpha=0.7)
    axes[2,1].set_title('Velocity Bode - Phase')
    axes[2,1].set_xlabel('Frequency (rad/s)')
    axes[2,1].set_ylabel('Phase (degrees)')
    axes[2,1].grid(True)
    
    plt.tight_layout()
    
    if save_plots:
        plt.savefig('ball_screw_analysis.png', dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Print system characteristics
    print(f"System Characteristics:")
    print(f"Time constant: {ballscrew.time_constant:.3f} s")
    print(f"DC gain (velocity): {ballscrew.dc_gain_velocity:.4f} (m/s)/N")
    print(f"Corner frequency: {ballscrew.B/ballscrew.M:.3f} rad/s")
    print(f"Poles: {ballscrew.poles_position}")

def demonstrate_tracking_performance(ballscrew):
    """
    Demonstrate tracking performance for different reference trajectories
    
    ## Tracking Performance Analysis
    
    Shows how well the ball screw can track different types of reference trajectories:
    1. Step position - requires impulse force
    2. Ramp position - requires step force
    3. Parabolic position - requires ramp force
    4. Sinusoidal position - requires sinusoidal force with specific amplitude/phase
    """
    
    print("\n=== Tracking Performance Analysis ===")
    
    t = np.linspace(0, 10, 1000)
    dt = t[1] - t[0]
    
    # Different reference trajectories
    trajectories = {
        'Step': np.ones_like(t) * 0.1,  # 0.1 m step
        'Ramp': 0.02 * t,  # 0.02 m/s ramp
        'Parabolic': 0.005 * t**2,  # 0.01 m/s² acceleration
        'Sinusoidal': 0.05 * (1 - np.cos(2*np.pi*0.2*t))  # 0.2 Hz sine
    }
    
    fig, axes = plt.subplots(4, 2, figsize=(15, 16))
    fig.suptitle('Ball Screw Tracking Performance', fontsize=16)
    
    for i, (traj_name, reference) in enumerate(trajectories.items()):
        # Calculate required force and tracking performance
        required_force, tracking_error, vel_ref, acc_ref = ballscrew.analyze_tracking_performance(reference, t)
        
        # Simulate actual response
        _, actual_position = ballscrew.simulate_position(required_force, t)
        
        # Plot reference vs actual position
        axes[i,0].plot(t, reference, 'r--', label='Reference', linewidth=2)
        axes[i,0].plot(t, actual_position, 'b-', label='Actual', linewidth=2)
        axes[i,0].set_title(f'{traj_name} Position Tracking')
        axes[i,0].set_ylabel('Position (m)')
        axes[i,0].legend()
        axes[i,0].grid(True)
        
        # Plot required force
        axes[i,1].plot(t, required_force, 'g-', linewidth=2)
        axes[i,1].set_title(f'{traj_name} Required Force')
        axes[i,1].set_ylabel('Force (N)')
        axes[i,1].grid(True)
        
        if i == 3:  # Last subplot
            axes[i,0].set_xlabel('Time (s)')
            axes[i,1].set_xlabel('Time (s)')
        
        # Print tracking statistics
        max_error = np.max(np.abs(tracking_error))
        rms_error = np.sqrt(np.mean(tracking_error**2))
        max_force = np.max(np.abs(required_force))
        
        print(f"{traj_name} Tracking:")
        print(f"  Max error: {max_error:.6f} m")
        print(f"  RMS error: {rms_error:.6f} m")
        print(f"  Max force: {max_force:.2f} N")
    
    plt.tight_layout()
    plt.show()

def compare_ballscrew_configurations():
    """
    Compare different ball screw configurations
    
    ## Configuration Comparison
    
    Compares systems with different mass and damping characteristics:
    - Light, low damping: Fast response, low force requirements
    - Heavy, high damping: Slow response, high force requirements
    - Different M/B ratios affect time constant and tracking performance
    """
    
    print("\n=== Ball Screw Configuration Comparison ===")
    
    configurations = [
        (5.0, 25.0, "Light, Low Damping"),
        (10.0, 50.0, "Standard"),
        (20.0, 100.0, "Heavy, High Damping"),
        (10.0, 25.0, "Low Damping"),
        (10.0, 100.0, "High Damping")
    ]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Ball Screw Configuration Comparison', fontsize=14)
    
    # Step responses
    for M, B, label in configurations:
        ballscrew = BallScrew(M=M, B=B)
        
        # Position step response
        t_pos, y_pos = ballscrew.step_response_position(t_span=20)
        axes[0,0].plot(t_pos, y_pos, label=f'{label} (τ={ballscrew.time_constant:.1f}s)')
        
        # Velocity step response
        t_vel, y_vel = ballscrew.step_response_velocity(t_span=10)
        axes[0,1].plot(t_vel, y_vel, label=f'{label} (K={ballscrew.dc_gain_velocity:.3f})')
    
    axes[0,0].set_title('Position Step Responses')
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Position (m)')
    axes[0,0].legend()
    axes[0,0].grid(True)
    
    axes[0,1].set_title('Velocity Step Responses')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Velocity (m/s)')
    axes[0,1].legend()
    axes[0,1].grid(True)
    
    # Frequency responses
    for M, B, label in configurations:
        ballscrew = BallScrew(M=M, B=B)
        
        # Position frequency response
        freq_pos, mag_pos, _ = ballscrew.frequency_response_position()
        axes[1,0].loglog(freq_pos, np.abs(mag_pos), label=label)
        
        # Velocity frequency response
        freq_vel, mag_vel, _ = ballscrew.frequency_response_velocity()
        axes[1,1].loglog(freq_vel, np.abs(mag_vel), label=label)
    
    axes[1,0].set_title('Position Frequency Response')
    axes[1,0].set_xlabel('Frequency (rad/s)')
    axes[1,0].set_ylabel('Magnitude')
    axes[1,0].legend()
    axes[1,0].grid(True)
    
    axes[1,1].set_title('Velocity Frequency Response')
    axes[1,1].set_xlabel('Frequency (rad/s)')
    axes[1,1].set_ylabel('Magnitude')
    axes[1,1].legend()
    axes[1,1].grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Print configuration characteristics
    print("Configuration Characteristics:")
    for M, B, label in configurations:
        ballscrew = BallScrew(M=M, B=B)
        print(f"{label:20s}: τ={ballscrew.time_constant:5.2f}s, "
              f"K={ballscrew.dc_gain_velocity:7.4f}(m/s)/N, "
              f"BW={1/ballscrew.time_constant:5.2f}rad/s")

def main():
    """
    ## Main Simulation and Analysis
    
    This section demonstrates:
    1. Ball screw modeling with different parameters
    2. System identification from simulated data
    3. Tracking performance analysis
    4. Configuration comparison
    5. Comprehensive analysis and visualization
    """
    
    print("=== Ball Screw System Analysis ===\n")
    
    # Create ball screw systems with different characteristics
    
    # Precision positioning system (CNC machine)
    print("1. Precision Positioning (CNC Machine):")
    ballscrew_cnc = BallScrew(M=15.0, B=75.0)
    plot_ballscrew_analysis(ballscrew_cnc)
    
    # 3D printer Z-axis
    print("\n2. 3D Printer Z-axis:")
    ballscrew_3d = BallScrew(M=2.0, B=10.0)
    plot_ballscrew_analysis(ballscrew_3d)
    
    # Heavy-duty linear actuator
    print("\n3. Heavy-duty Linear Actuator:")
    ballscrew_heavy = BallScrew(M=50.0, B=200.0)
    plot_ballscrew_analysis(ballscrew_heavy)
    
    # Tracking performance demonstration
    demonstrate_tracking_performance(ballscrew_cnc)
    
    # Configuration comparison
    compare_ballscrew_configurations()
    
    # System identification example
    print("\n=== System Identification Example ===")
    
    # Generate synthetic data from known system
    true_ballscrew = BallScrew(M=12.0, B=60.0)
    t_data = np.linspace(0, 15, 750)
    
    # Test with both velocity and position data
    force_input = np.ones_like(t_data) * 100  # 100N step input
    
    # Velocity identification
    _, v_data = true_ballscrew.simulate_velocity(force_input, t_data)
    v_noise = 0.02 * np.max(v_data) * np.random.randn(len(v_data))
    v_data_noisy = v_data + v_noise
    
    M_est_vel, B_est_vel = system_identification_ballscrew(force_input, v_data_noisy, 
                                                          t_data, 'velocity')
    
    # Position identification
    _, p_data = true_ballscrew.simulate_position(force_input, t_data)
    p_noise = 0.001 * np.max(p_data) * np.random.randn(len(p_data))
    p_data_noisy = p_data + p_noise
    
    M_est_pos, B_est_pos = system_identification_ballscrew(force_input, p_data_noisy, 
                                                          t_data, 'position')
    
    print(f"\\nTrue parameters: M={true_ballscrew.M} kg, B={true_ballscrew.B} N·s/m")
    print(f"Velocity ID: M={M_est_vel:.1f} kg, B={B_est_vel:.1f} N·s/m")
    print(f"Position ID: M={M_est_pos:.1f} kg, B={B_est_pos:.1f} N·s/m")
    
    # Errors
    error_M_vel = abs(M_est_vel - true_ballscrew.M) / true_ballscrew.M * 100
    error_B_vel = abs(B_est_vel - true_ballscrew.B) / true_ballscrew.B * 100
    error_M_pos = abs(M_est_pos - true_ballscrew.M) / true_ballscrew.M * 100
    error_B_pos = abs(B_est_pos - true_ballscrew.B) / true_ballscrew.B * 100
    
    print(f"Velocity ID errors: ΔM={error_M_vel:.1f}%, ΔB={error_B_vel:.1f}%")
    print(f"Position ID errors: ΔM={error_M_pos:.1f}%, ΔB={error_B_pos:.1f}%")
    
    # Compare responses
    estimated_ballscrew_vel = BallScrew(M=M_est_vel, B=B_est_vel)
    estimated_ballscrew_pos = BallScrew(M=M_est_pos, B=B_est_pos)
    
    _, v_est_vel = estimated_ballscrew_vel.simulate_velocity(force_input, t_data)
    _, p_est_pos = estimated_ballscrew_pos.simulate_position(force_input, t_data)
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Velocity comparison
    axes[0].plot(t_data, v_data, 'b-', label='True System', linewidth=2)
    axes[0].plot(t_data, v_data_noisy, 'r.', label='Noisy Data', alpha=0.6, markersize=1)
    axes[0].plot(t_data, v_est_vel, 'g--', label='Identified (Velocity)', linewidth=2)
    axes[0].set_ylabel('Velocity (m/s)')
    axes[0].set_title('Velocity System Identification Results')
    axes[0].legend()
    axes[0].grid(True)
    
    # Position comparison
    axes[1].plot(t_data, p_data, 'b-', label='True System', linewidth=2)
    axes[1].plot(t_data, p_data_noisy, 'r.', label='Noisy Data', alpha=0.6, markersize=1)
    axes[1].plot(t_data, p_est_pos, 'g--', label='Identified (Position)', linewidth=2)
    axes[1].set_ylabel('Position (m)')
    axes[1].set_xlabel('Time (s)')
    axes[1].set_title('Position System Identification Results')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Performance metrics
    vel_rmse = np.sqrt(np.mean((v_data - v_est_vel)**2))
    pos_rmse = np.sqrt(np.mean((p_data - p_est_pos)**2))
    
    print(f"\\nIdentification Performance:")
    print(f"Velocity RMSE: {vel_rmse:.6f} m/s")
    print(f"Position RMSE: {pos_rmse:.6f} m")

if __name__ == "__main__":
    main()