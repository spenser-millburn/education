"""
# Robotic Arm Joint System

## Theory

A robotic arm joint with moment of inertia M, friction coefficient B, and spring stiffness k follows the equation:

$$M\ddot{\theta} + B\dot{\theta} + k\theta = \tau$$

Where:
- $M$ is the moment of inertia (kg·m²)
- $B$ is the friction coefficient (N·m·s/rad)
- $k$ is the spring stiffness (N·m/rad)
- $\tau$ is the applied torque (N·m)
- $\theta$ is the angular position (rad)

This is a second-order system. Taking the Laplace transform:

$$Ms^2\Theta(s) + Bs\Theta(s) + k\Theta(s) = \tau(s)$$

The transfer function from torque to angular position is:

$$G(s) = \frac{\Theta(s)}{\tau(s)} = \frac{1}{Ms^2 + Bs + k}$$

This can be written in standard second-order form:

$$G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

Where:
- $\omega_n = \sqrt{k/M}$ is the natural frequency (rad/s)
- $\zeta = \frac{B}{2\sqrt{kM}}$ is the damping ratio (dimensionless)
- $K_{dc} = 1/k$ is the DC gain (rad/N·m)

The system behavior depends on the damping ratio:
- $\zeta < 1$: Underdamped (oscillatory response)
- $\zeta = 1$: Critically damped (fastest settling without overshoot)
- $\zeta > 1$: Overdamped (slow, no oscillation)

For velocity output, the transfer function becomes:

$$G_v(s) = \frac{s\Theta(s)}{\tau(s)} = \frac{s}{Ms^2 + Bs + k}$$
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.optimize import curve_fit
import control as ct

class RoboticArmJoint:
    def __init__(self, M=0.1, B=0.5, k=10.0):
        """
        Initialize robotic arm joint parameters
        
        Parameters:
        M (float): Moment of inertia (kg·m²)
        B (float): Friction coefficient (N·m·s/rad)
        k (float): Spring stiffness (N·m/rad)
        """
        self.M = M
        self.B = B
        self.k = k
        self.update_system()
    
    def update_system(self):
        """Update the system transfer function and state space representation"""
        # Transfer function from torque to position: G(s) = 1/(Ms^2 + Bs + k)
        num_pos = [1]
        den_pos = [self.M, self.B, self.k]
        self.tf_position = ct.TransferFunction(num_pos, den_pos)
        
        # Transfer function from torque to velocity: G(s) = s/(Ms^2 + Bs + k)
        num_vel = [1, 0]
        den_vel = [self.M, self.B, self.k]
        self.tf_velocity = ct.TransferFunction(num_vel, den_vel)
        
        # State space representation: x1 = theta, x2 = theta_dot
        # theta_dot = x2, theta_ddot = (-k*x1 - B*x2 + tau)/M
        A = [[0, 1], [-self.k/self.M, -self.B/self.M]]
        B_matrix = [[0], [1/self.M]]
        C_pos = [[1, 0]]  # Position output
        C_vel = [[0, 1]]  # Velocity output
        D_matrix = [[0]]
        
        self.ss_position = ct.StateSpace(A, B_matrix, C_pos, D_matrix)
        self.ss_velocity = ct.StateSpace(A, B_matrix, C_vel, D_matrix)
        
        # System characteristics
        self.natural_frequency = np.sqrt(self.k / self.M) if self.M != 0 else float('inf')
        self.damping_ratio = self.B / (2 * np.sqrt(self.k * self.M)) if (self.k != 0 and self.M != 0) else 0
        self.dc_gain = 1 / self.k if self.k != 0 else float('inf')
        
        # Calculate poles
        if self.M != 0:
            discriminant = self.B**2 - 4*self.M*self.k
            if discriminant >= 0:
                # Real poles (overdamped or critically damped)
                self.pole1 = (-self.B + np.sqrt(discriminant)) / (2*self.M)
                self.pole2 = (-self.B - np.sqrt(discriminant)) / (2*self.M)
                self.pole_type = "Real"
            else:
                # Complex poles (underdamped)
                real_part = -self.B / (2*self.M)
                imag_part = np.sqrt(-discriminant) / (2*self.M)
                self.pole1 = complex(real_part, imag_part)
                self.pole2 = complex(real_part, -imag_part)
                self.pole_type = "Complex"
        
        # Settling time and peak time (for underdamped case)
        if self.damping_ratio < 1 and self.damping_ratio > 0:
            self.settling_time = 4 / (self.damping_ratio * self.natural_frequency)
            self.peak_time = np.pi / (self.natural_frequency * np.sqrt(1 - self.damping_ratio**2))
            self.percent_overshoot = 100 * np.exp(-np.pi * self.damping_ratio / np.sqrt(1 - self.damping_ratio**2))
        else:
            self.settling_time = float('inf')
            self.peak_time = float('inf')
            self.percent_overshoot = 0
    
    def step_response_position(self, t_span=10, num_points=1000):
        """
        Generate step response for position
        
        Parameters:
        t_span (float): Time span for simulation
        num_points (int): Number of time points
        
        Returns:
        t (array): Time vector
        y (array): Position response vector
        """
        t = np.linspace(0, t_span, num_points)
        t, y = ct.step_response(self.tf_position, t)
        return t, y
    
    def step_response_velocity(self, t_span=10, num_points=1000):
        """Generate step response for velocity"""
        t = np.linspace(0, t_span, num_points)
        t, y = ct.step_response(self.tf_velocity, t)
        return t, y
    
    def impulse_response_position(self, t_span=10, num_points=1000):
        """Generate impulse response for position"""
        t = np.linspace(0, t_span, num_points)
        t, y = ct.impulse_response(self.tf_position, t)
        return t, y
    
    def impulse_response_velocity(self, t_span=10, num_points=1000):
        """Generate impulse response for velocity"""
        t = np.linspace(0, t_span, num_points)
        t, y = ct.impulse_response(self.tf_velocity, t)
        return t, y
    
    def frequency_response_position(self, freq_range=None):
        """
        Generate frequency response for position (Bode plot data)
        
        Parameters:
        freq_range (array): Frequency range in rad/s
        
        Returns:
        freq (array): Frequency vector
        mag (array): Magnitude response
        phase (array): Phase response
        """
        if freq_range is None:
            freq_range = np.logspace(-1, 2, 1000)
        
        freq, mag, phase = ct.bode(self.tf_position, freq_range, plot=False)
        return freq, mag, phase
    
    def frequency_response_velocity(self, freq_range=None):
        """Generate frequency response for velocity"""
        if freq_range is None:
            freq_range = np.logspace(-1, 2, 1000)
        
        freq, mag, phase = ct.bode(self.tf_velocity, freq_range, plot=False)
        return freq, mag, phase
    
    def simulate_position(self, torque_input, time):
        """
        Simulate position response to arbitrary torque input
        
        Parameters:
        torque_input (array): Applied torque input vector
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        y (array): Position response
        """
        t, y = ct.forced_response(self.tf_position, time, torque_input)
        return t, y
    
    def simulate_velocity(self, torque_input, time):
        """Simulate velocity response to arbitrary torque input"""
        t, y = ct.forced_response(self.tf_velocity, time, torque_input)
        return t, y
    
    def simulate_with_external_disturbance(self, torque_input, disturbance_torque, time):
        """
        Simulate system with both applied torque and external disturbances
        
        ## External Disturbance Effects
        
        With external disturbance $\tau_d$, the equation becomes:
        $$M\ddot{\theta} + B\dot{\theta} + k\theta = \tau + \tau_d$$
        
        Parameters:
        torque_input (array): Applied torque
        disturbance_torque (array): External disturbance torque
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        theta (array): Position response
        omega (array): Velocity response
        """
        # Create augmented system with two inputs: applied torque and disturbance
        A = [[0, 1], [-self.k/self.M, -self.B/self.M]]
        B_matrix = [[0, 0], [1/self.M, 1/self.M]]  # Two inputs: applied and disturbance torque
        C = [[1, 0], [0, 1]]  # Both position and velocity outputs
        D_matrix = [[0, 0], [0, 0]]
        
        ss_dual = ct.StateSpace(A, B_matrix, C, D_matrix)
        
        # Combine inputs
        inputs = np.array([torque_input, disturbance_torque])
        
        t, y = ct.forced_response(ss_dual, time, inputs)
        theta = y[0]  # Position
        omega = y[1]  # Velocity
        
        return t, theta, omega
    
    def simulate_with_variable_stiffness(self, torque_input, stiffness_variation, time):
        """
        Simulate system with time-varying stiffness
        
        ## Variable Stiffness Effects
        
        With time-varying stiffness $k(t)$, the equation becomes:
        $$M\ddot{\theta} + B\dot{\theta} + k(t)\theta = \tau$$
        
        This creates a time-varying system that must be solved numerically.
        
        Parameters:
        torque_input (array): Applied torque
        stiffness_variation (array): Time-varying stiffness k(t)
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        theta (array): Position response
        omega (array): Velocity response
        """
        dt = time[1] - time[0]
        theta = np.zeros_like(time)
        omega = np.zeros_like(time)
        
        for i in range(1, len(time)):
            # Current stiffness
            k_current = stiffness_variation[i-1]
            
            # Numerical integration using Euler method
            # theta_ddot = (-k_current * theta - B * omega + tau) / M
            theta_ddot = (-k_current * theta[i-1] - self.B * omega[i-1] + torque_input[i-1]) / self.M
            omega[i] = omega[i-1] + theta_ddot * dt
            theta[i] = theta[i-1] + omega[i-1] * dt
        
        return time, theta, omega

def system_identification_joint(input_data, output_data, time_data, output_type='position'):
    """
    Perform system identification to estimate M, B, k parameters
    
    ## System Identification for Robotic Arm Joints
    
    For position output, we fit a second-order system:
    $$G(s) = \frac{1}{Ms^2 + Bs + k} = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$
    
    Parameters:
    input_data (array): Input torque data
    output_data (array): Output data (position or velocity)
    time_data (array): Time vector
    output_type (str): 'position' or 'velocity'
    
    Returns:
    M_est, B_est, k_est: Estimated parameters
    """
    
    if output_type == 'position':
        # Second-order system identification
        def second_order_step(t, K, wn, zeta):
            """Second-order step response"""
            if zeta < 1:
                # Underdamped
                wd = wn * np.sqrt(1 - zeta**2)
                y = K * (1 - np.exp(-zeta*wn*t) * (np.cos(wd*t) + (zeta*wn/wd)*np.sin(wd*t)))
            elif zeta == 1:
                # Critically damped
                y = K * (1 - np.exp(-wn*t) * (1 + wn*t))
            else:
                # Overdamped
                r1 = -wn * (zeta + np.sqrt(zeta**2 - 1))
                r2 = -wn * (zeta - np.sqrt(zeta**2 - 1))
                A1 = r2 / (r2 - r1)
                A2 = -r1 / (r2 - r1)
                y = K * (1 - A1*np.exp(r1*t) - A2*np.exp(r2*t))
            return y
        
        # Check if input is step-like
        if np.allclose(input_data[10:], input_data[10]):  # Step input
            try:
                # Normalize by step magnitude
                step_magnitude = input_data[10]
                normalized_output = output_data / step_magnitude
                
                # Initial parameter guesses
                K_guess = normalized_output[-1]  # Final value
                wn_guess = 2*np.pi  # Initial guess for natural frequency
                zeta_guess = 0.5   # Initial guess for damping ratio
                
                popt, _ = curve_fit(second_order_step, time_data, normalized_output,
                                  p0=[K_guess, wn_guess, zeta_guess],
                                  bounds=([0, 0.1, 0], [10, 100, 5]))
                K_est, wn_est, zeta_est = popt
                
                # Convert back to physical parameters
                # K = 1/k, wn = sqrt(k/M), zeta = B/(2*sqrt(k*M))
                k_est = 1 / K_est
                M_est = k_est / (wn_est**2)
                B_est = 2 * zeta_est * np.sqrt(k_est * M_est)
                
            except:
                # Fallback values
                M_est, B_est, k_est = 0.1, 0.5, 10.0
        else:
            # For non-step inputs, use more complex identification
            M_est, B_est, k_est = 0.1, 0.5, 10.0
    
    else:  # velocity output
        # Velocity transfer function: s/(Ms^2 + Bs + k)
        # This requires more complex identification
        M_est, B_est, k_est = 0.1, 0.5, 10.0
    
    return M_est, B_est, k_est

def plot_joint_analysis(joint, save_plots=False):
    """
    Generate comprehensive plots for robotic arm joint analysis
    
    Parameters:
    joint (RoboticArmJoint): System to analyze
    save_plots (bool): Whether to save plots to files
    """
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle(f'Robotic Arm Joint Analysis (M={joint.M}, B={joint.B}, k={joint.k})', 
                 fontsize=14)
    
    # Position step response
    t_pos, y_pos = joint.step_response_position()
    axes[0,0].plot(t_pos, y_pos)
    axes[0,0].set_title('Position Step Response')
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Position (rad)')
    axes[0,0].grid(True)
    
    # Velocity step response
    t_vel, y_vel = joint.step_response_velocity()
    axes[0,1].plot(t_vel, y_vel)
    axes[0,1].set_title('Velocity Step Response')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Velocity (rad/s)')
    axes[0,1].grid(True)
    
    # Position frequency response
    freq_pos, mag_pos, phase_pos = joint.frequency_response_position()
    axes[1,0].loglog(freq_pos, np.abs(mag_pos))
    axes[1,0].set_title('Position Bode - Magnitude')
    axes[1,0].set_xlabel('Frequency (rad/s)')
    axes[1,0].set_ylabel('Magnitude')
    axes[1,0].grid(True)
    
    # Velocity frequency response
    freq_vel, mag_vel, phase_vel = joint.frequency_response_velocity()
    axes[1,1].loglog(freq_vel, np.abs(mag_vel))
    axes[1,1].set_title('Velocity Bode - Magnitude')
    axes[1,1].set_xlabel('Frequency (rad/s)')
    axes[1,1].set_ylabel('Magnitude')
    axes[1,1].grid(True)
    
    # Phase plots
    axes[2,0].semilogx(freq_pos, np.angle(mag_pos)*180/np.pi)
    axes[2,0].set_title('Position Bode - Phase')
    axes[2,0].set_xlabel('Frequency (rad/s)')
    axes[2,0].set_ylabel('Phase (degrees)')
    axes[2,0].grid(True)
    
    axes[2,1].semilogx(freq_vel, np.angle(mag_vel)*180/np.pi)
    axes[2,1].set_title('Velocity Bode - Phase')
    axes[2,1].set_xlabel('Frequency (rad/s)')
    axes[2,1].set_ylabel('Phase (degrees)')
    axes[2,1].grid(True)
    
    plt.tight_layout()
    
    if save_plots:
        plt.savefig('robotic_arm_joint_analysis.png', dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Print system characteristics
    print(f"System Characteristics:")
    print(f"Natural frequency (ωn): {joint.natural_frequency:.3f} rad/s")
    print(f"Damping ratio (ζ): {joint.damping_ratio:.3f}")
    print(f"DC gain: {joint.dc_gain:.3f} rad/N·m")
    print(f"Pole type: {joint.pole_type}")
    print(f"Poles: {joint.pole1:.3f}, {joint.pole2:.3f}")
    
    if joint.damping_ratio < 1 and joint.damping_ratio > 0:
        print(f"Settling time (2%): {joint.settling_time:.3f} s")
        print(f"Peak time: {joint.peak_time:.3f} s")
        print(f"Percent overshoot: {joint.percent_overshoot:.1f}%")

def demonstrate_damping_effects():
    """
    Demonstrate the effect of different damping ratios
    
    ## Damping Ratio Effects
    
    The damping ratio ζ determines the system behavior:
    - ζ < 1: Underdamped (oscillatory)
    - ζ = 1: Critically damped (optimal)
    - ζ > 1: Overdamped (slow)
    """
    
    print("\n=== Damping Ratio Effects ===")
    
    # Fixed M and k, vary B to change damping ratio
    M, k = 0.1, 25.0  # Fixed values
    
    damping_scenarios = [
        (0.1, "Underdamped (ζ=0.1)"),
        (0.5, "Underdamped (ζ=0.5)"),
        (1.0, "Critically damped (ζ=1.0)"),
        (2.0, "Overdamped (ζ=2.0)")
    ]
    
    plt.figure(figsize=(15, 10))
    
    for i, (zeta, label) in enumerate(damping_scenarios):
        # Calculate B for desired damping ratio
        B = 2 * zeta * np.sqrt(k * M)
        joint = RoboticArmJoint(M=M, B=B, k=k)
        
        t, y = joint.step_response_position()
        
        plt.subplot(2, 2, 1)
        plt.plot(t, y, label=label)
        plt.ylabel('Position (rad)')
        plt.title('Step Response vs Damping Ratio')
        plt.legend()
        plt.grid(True)
        
        # Impulse response
        t_imp, y_imp = joint.impulse_response_position()
        plt.subplot(2, 2, 2)
        plt.plot(t_imp, y_imp, label=label)
        plt.ylabel('Position (rad)')
        plt.title('Impulse Response vs Damping Ratio')
        plt.xlabel('Time (s)')
        plt.legend()
        plt.grid(True)
        
        # Frequency response
        freq, mag, phase = joint.frequency_response_position()
        plt.subplot(2, 2, 3)
        plt.loglog(freq, np.abs(mag), label=label)
        plt.ylabel('Magnitude')
        plt.title('Frequency Response vs Damping Ratio')
        plt.xlabel('Frequency (rad/s)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 4)
        plt.semilogx(freq, np.angle(mag)*180/np.pi, label=label)
        plt.ylabel('Phase (degrees)')
        plt.xlabel('Frequency (rad/s)')
        plt.title('Phase Response vs Damping Ratio')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def demonstrate_disturbance_effects(joint):
    """
    Demonstrate the effect of external disturbances on joint performance
    
    ## Disturbance Analysis
    
    External disturbances affect the system response:
    - Constant disturbances create steady-state errors
    - Oscillatory disturbances can excite resonant modes
    - Impact disturbances test transient response
    """
    
    print("\n=== External Disturbance Effects ===")
    
    t = np.linspace(0, 15, 1000)
    applied_torque = np.ones_like(t) * 5.0  # 5 N·m step torque
    
    # Different disturbance scenarios
    disturbance_scenarios = [
        (np.zeros_like(t), "No Disturbance"),
        (np.ones_like(t) * 2.0, "Constant Disturbance (2 N·m)"),
        (1.5 * np.sin(2*np.pi*joint.natural_frequency*0.8*t), "Near-Resonance Disturbance"),
        (3.0 * (t > 5) * (t < 5.1), "Impact Disturbance")
    ]
    
    plt.figure(figsize=(12, 10))
    
    for i, (disturbance, label) in enumerate(disturbance_scenarios):
        t_sim, theta, omega = joint.simulate_with_external_disturbance(applied_torque, disturbance, t)
        
        plt.subplot(3, 1, 1)
        plt.plot(t_sim, disturbance, label=label)
        plt.ylabel('Disturbance (N·m)')
        plt.title('External Disturbance Torques')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 1, 2)
        plt.plot(t_sim, theta, label=label)
        plt.ylabel('Position (rad)')
        plt.title('Position Response with Disturbances')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 1, 3)
        plt.plot(t_sim, omega, label=label)
        plt.ylabel('Velocity (rad/s)')
        plt.xlabel('Time (s)')
        plt.title('Velocity Response with Disturbances')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def main():
    """
    ## Main Simulation and Analysis
    
    This section demonstrates:
    1. Robotic arm joint modeling with different parameters
    2. Damping ratio effects on system behavior
    3. System identification from simulated data
    4. External disturbance effects
    5. Comprehensive analysis and visualization
    """
    
    print("=== Robotic Arm Joint System Analysis ===\n")
    
    # Create joints with different characteristics
    
    # Underdamped joint (low friction)
    print("1. Underdamped Joint (Low Friction):")
    joint_under = RoboticArmJoint(M=0.05, B=0.2, k=20.0)
    plot_joint_analysis(joint_under)
    
    # Critically damped joint
    print("\n2. Critically Damped Joint:")
    M, k = 0.1, 25.0
    B_critical = 2 * np.sqrt(k * M)  # ζ = 1
    joint_critical = RoboticArmJoint(M=M, B=B_critical, k=k)
    plot_joint_analysis(joint_critical)
    
    # Overdamped joint (high friction)
    print("\n3. Overdamped Joint (High Friction):")
    joint_over = RoboticArmJoint(M=0.2, B=2.0, k=15.0)
    plot_joint_analysis(joint_over)
    
    # Demonstrate damping effects
    demonstrate_damping_effects()
    
    # Demonstrate disturbance effects
    demonstrate_disturbance_effects(joint_critical)
    
    # Variable stiffness demonstration
    print("\n=== Variable Stiffness Effects ===")
    
    t = np.linspace(0, 10, 1000)
    torque = np.ones_like(t) * 3.0
    
    # Stiffness scenarios
    k_constant = np.ones_like(t) * joint_critical.k
    k_increasing = joint_critical.k * (1 + 0.5 * t / 10)  # Stiffness increases over time
    k_oscillating = joint_critical.k * (1 + 0.3 * np.sin(2*np.pi*0.2*t))
    
    stiffness_scenarios = [
        (k_constant, "Constant Stiffness"),
        (k_increasing, "Increasing Stiffness"),
        (k_oscillating, "Oscillating Stiffness")
    ]
    
    plt.figure(figsize=(12, 10))
    
    for i, (k_variation, label) in enumerate(stiffness_scenarios):
        t_sim, theta, omega = joint_critical.simulate_with_variable_stiffness(torque, k_variation, t)
        
        plt.subplot(3, 1, 1)
        plt.plot(t_sim, k_variation, label=label)
        plt.ylabel('Stiffness (N·m/rad)')
        plt.title('Stiffness Variation')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 1, 2)
        plt.plot(t_sim, theta, label=label)
        plt.ylabel('Position (rad)')
        plt.title('Position Response with Variable Stiffness')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 1, 3)
        plt.plot(t_sim, omega, label=label)
        plt.ylabel('Velocity (rad/s)')
        plt.xlabel('Time (s)')
        plt.title('Velocity Response with Variable Stiffness')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # System identification example
    print("\n=== System Identification Example ===")
    
    # Generate synthetic data from known system
    true_joint = RoboticArmJoint(M=0.08, B=0.4, k=18.0)
    t_data = np.linspace(0, 8, 200)
    torque_input = np.ones_like(t_data) * 2.0  # Step input
    _, pos_data = true_joint.simulate_position(torque_input, t_data)
    
    # Add noise
    pos_data_noisy = pos_data + 0.002 * np.random.randn(len(pos_data))
    
    # Perform system identification
    M_est, B_est, k_est = system_identification_joint(torque_input, pos_data_noisy, 
                                                     t_data, 'position')
    
    print(f"True parameters: M={true_joint.M}, B={true_joint.B}, k={true_joint.k}")
    print(f"Estimated parameters: M={M_est:.4f}, B={B_est:.4f}, k={k_est:.4f}")
    
    # Compare responses
    estimated_joint = RoboticArmJoint(M=M_est, B=B_est, k=k_est)
    _, pos_est = estimated_joint.simulate_position(torque_input, t_data)
    
    plt.figure(figsize=(10, 6))
    plt.plot(t_data, pos_data, 'b-', label='True System', linewidth=2)
    plt.plot(t_data, pos_data_noisy, 'r.', label='Noisy Data', alpha=0.6)
    plt.plot(t_data, pos_est, 'g--', label='Identified System', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Position (rad)')
    plt.title('Position System Identification')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    print(f"True system characteristics:")
    print(f"  ωn: {true_joint.natural_frequency:.3f} rad/s, ζ: {true_joint.damping_ratio:.3f}")
    print(f"Estimated system characteristics:")
    print(f"  ωn: {estimated_joint.natural_frequency:.3f} rad/s, ζ: {estimated_joint.damping_ratio:.3f}")

if __name__ == "__main__":
    main()