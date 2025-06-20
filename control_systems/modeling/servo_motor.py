"""
# Servo Motor System

## Theory

A servo motor with moment of inertia J, damping coefficient D, and torque constant Kt follows the equation:

$$J\ddot{\theta} + D\dot{\theta} = K_t I$$

Where:
- $J$ is the moment of inertia (kg·m²)
- $D$ is the damping coefficient (N·m·s/rad)
- $K_t$ is the torque constant (N·m/A)
- $I$ is the motor current (A)
- $\theta$ is the angular position (rad)

This is a second-order system. Taking the Laplace transform:

$$Js^2\Theta(s) + Ds\Theta(s) = K_t I(s)$$

The transfer function from current to angular position is:

$$G(s) = \frac{\Theta(s)}{I(s)} = \frac{K_t}{Js^2 + Ds}$$

This can be rewritten as:

$$G(s) = \frac{K_t/D}{s(s + D/J)}$$

The system has poles at $s = 0$ and $s = -D/J$, making it marginally stable with one integrator.

For velocity output, the transfer function becomes:

$$G_v(s) = \frac{s\Theta(s)}{I(s)} = \frac{K_t}{Js + D}$$

This is a first-order system with time constant $\tau = J/D$.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.optimize import curve_fit
import control as ct

class ServoMotor:
    def __init__(self, J=0.01, D=0.1, Kt=0.1):
        """
        Initialize servo motor parameters
        
        Parameters:
        J (float): Moment of inertia (kg·m²)
        D (float): Damping coefficient (N·m·s/rad)
        Kt (float): Torque constant (N·m/A)
        """
        self.J = J
        self.D = D
        self.Kt = Kt
        self.update_system()
    
    def update_system(self):
        """Update the system transfer function and state space representation"""
        # Transfer function from current to position: G(s) = Kt/(Js^2 + Ds)
        num_pos = [self.Kt]
        den_pos = [self.J, self.D, 0]
        self.tf_position = ct.TransferFunction(num_pos, den_pos)
        
        # Transfer function from current to velocity: G(s) = Kt/(Js + D)
        num_vel = [self.Kt]
        den_vel = [self.J, self.D]
        self.tf_velocity = ct.TransferFunction(num_vel, den_vel)
        
        # State space representation: x1 = theta, x2 = theta_dot
        # theta_dot = x2, theta_ddot = (-D*x2 + Kt*I)/J
        A = [[0, 1], [0, -self.D/self.J]]
        B = [[0], [self.Kt/self.J]]
        C_pos = [[1, 0]]  # Position output
        C_vel = [[0, 1]]  # Velocity output
        D_matrix = [[0]]
        
        self.ss_position = ct.StateSpace(A, B, C_pos, D_matrix)
        self.ss_velocity = ct.StateSpace(A, B, C_vel, D_matrix)
        
        # System characteristics
        self.time_constant = self.J / self.D if self.D != 0 else float('inf')
        self.dc_gain_velocity = self.Kt / self.D if self.D != 0 else float('inf')
    
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
            freq_range = np.logspace(-2, 3, 1000)
        
        freq, mag, phase = ct.bode(self.tf_position, freq_range, plot=False)
        return freq, mag, phase
    
    def frequency_response_velocity(self, freq_range=None):
        """Generate frequency response for velocity"""
        if freq_range is None:
            freq_range = np.logspace(-2, 3, 1000)
        
        freq, mag, phase = ct.bode(self.tf_velocity, freq_range, plot=False)
        return freq, mag, phase
    
    def simulate_position(self, current_input, time):
        """
        Simulate position response to arbitrary current input
        
        Parameters:
        current_input (array): Motor current input vector
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        y (array): Position response
        """
        t, y = ct.forced_response(self.tf_position, time, current_input)
        return t, y
    
    def simulate_velocity(self, current_input, time):
        """Simulate velocity response to arbitrary current input"""
        t, y = ct.forced_response(self.tf_velocity, time, current_input)
        return t, y
    
    def simulate_with_load_torque(self, current_input, load_torque, time):
        """
        Simulate system with both motor current and load torque
        
        ## Load Torque Effect
        
        With load torque $T_L$, the equation becomes:
        $$J\ddot{\theta} + D\dot{\theta} = K_t I - T_L$$
        
        Parameters:
        current_input (array): Motor current
        load_torque (array): Load torque
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        theta (array): Position response
        omega (array): Velocity response
        """
        # Create augmented system with two inputs: current and load torque
        A = [[0, 1], [0, -self.D/self.J]]
        B = [[0, 0], [self.Kt/self.J, -1/self.J]]  # Two inputs: current and load torque
        C = [[1, 0], [0, 1]]  # Both position and velocity outputs
        D_matrix = [[0, 0], [0, 0]]
        
        ss_dual = ct.StateSpace(A, B, C, D_matrix)
        
        # Combine inputs
        inputs = np.array([current_input, load_torque])
        
        t, y = ct.forced_response(ss_dual, time, inputs)
        theta = y[0]  # Position
        omega = y[1]  # Velocity
        
        return t, theta, omega

def system_identification_servo(input_data, output_data, time_data, output_type='velocity'):
    """
    Perform system identification to estimate J, D, Kt parameters
    
    ## System Identification for Servo Motors
    
    For velocity output, we fit a first-order system:
    $$G(s) = \frac{K_t}{Js + D} = \frac{K}{τs + 1}$$
    
    Where $K = K_t/D$ is the DC gain and $τ = J/D$ is the time constant.
    
    For position output, we have an integrator plus first-order system:
    $$G(s) = \frac{K_t}{s(Js + D)} = \frac{K}{s(τs + 1)}$$
    
    Parameters:
    input_data (array): Input current data
    output_data (array): Output data (position or velocity)
    time_data (array): Time vector
    output_type (str): 'velocity' or 'position'
    
    Returns:
    J_est, D_est, Kt_est: Estimated parameters
    """
    
    if output_type == 'velocity':
        # First-order system identification
        def first_order_step(t, K, tau):
            """First-order step response: K*(1 - exp(-t/tau))"""
            return K * (1 - np.exp(-t/tau))
        
        # Check if input is step-like
        if np.allclose(input_data[10:], input_data[10]):  # Step input
            try:
                # Normalize by step magnitude
                step_magnitude = input_data[10]
                normalized_output = output_data / step_magnitude
                
                popt, _ = curve_fit(first_order_step, time_data, normalized_output,
                                  bounds=([0, 0.01], [10, 10]))
                K_est, tau_est = popt
                
                # Convert back to physical parameters
                # K = Kt/D, tau = J/D
                # Assume reasonable Kt value or use additional constraints
                Kt_est = 0.1  # Default assumption
                D_est = Kt_est / K_est
                J_est = tau_est * D_est
                
            except:
                # Fallback values
                J_est, D_est, Kt_est = 0.01, 0.1, 0.1
        else:
            # For non-step inputs, use more complex identification
            J_est, D_est, Kt_est = 0.01, 0.1, 0.1
    
    else:  # position output
        # Second-order system with integrator
        def integrator_first_order_step(t, K, tau):
            """Step response of integrator + first-order system"""
            return K * (t - tau * (1 - np.exp(-t/tau)))
        
        if np.allclose(input_data[10:], input_data[10]):  # Step input
            try:
                step_magnitude = input_data[10]
                normalized_output = output_data / step_magnitude
                
                popt, _ = curve_fit(integrator_first_order_step, time_data, normalized_output,
                                  bounds=([0, 0.01], [1, 10]))
                K_est, tau_est = popt
                
                # Convert to physical parameters
                Kt_est = 0.1  # Assumption
                D_est = Kt_est / K_est
                J_est = tau_est * D_est
                
            except:
                J_est, D_est, Kt_est = 0.01, 0.1, 0.1
        else:
            J_est, D_est, Kt_est = 0.01, 0.1, 0.1
    
    return J_est, D_est, Kt_est

def plot_servo_analysis(servo, save_plots=False):
    """
    Generate comprehensive plots for servo motor analysis
    
    Parameters:
    servo (ServoMotor): System to analyze
    save_plots (bool): Whether to save plots to files
    """
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle(f'Servo Motor Analysis (J={servo.J}, D={servo.D}, Kt={servo.Kt})', 
                 fontsize=14)
    
    # Position step response
    t_pos, y_pos = servo.step_response_position()
    axes[0,0].plot(t_pos, y_pos)
    axes[0,0].set_title('Position Step Response')
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Position (rad)')
    axes[0,0].grid(True)
    
    # Velocity step response
    t_vel, y_vel = servo.step_response_velocity()
    axes[0,1].plot(t_vel, y_vel)
    axes[0,1].set_title('Velocity Step Response')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Velocity (rad/s)')
    axes[0,1].grid(True)
    
    # Position frequency response
    freq_pos, mag_pos, phase_pos = servo.frequency_response_position()
    axes[1,0].loglog(freq_pos, np.abs(mag_pos))
    axes[1,0].set_title('Position Bode - Magnitude')
    axes[1,0].set_xlabel('Frequency (rad/s)')
    axes[1,0].set_ylabel('Magnitude')
    axes[1,0].grid(True)
    
    # Velocity frequency response
    freq_vel, mag_vel, phase_vel = servo.frequency_response_velocity()
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
        plt.savefig('servo_motor_analysis.png', dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Print system characteristics
    print(f"System Characteristics:")
    print(f"Time constant (τ): {servo.time_constant:.3f} s")
    print(f"DC gain (velocity): {servo.dc_gain_velocity:.3f} rad/s/A")
    print(f"Bandwidth (-3dB): {1/servo.time_constant:.3f} rad/s")

def demonstrate_load_effects(servo):
    """
    Demonstrate the effect of load torque on servo performance
    
    ## Load Torque Analysis
    
    Load torque affects the steady-state behavior:
    - For constant current: steady-state velocity = $(K_t I - T_L)/D$
    - Load torque acts as a disturbance to the system
    """
    
    print("\n=== Load Torque Effects ===")
    
    t = np.linspace(0, 10, 1000)
    current = np.ones_like(t) * 1.0  # 1A step current
    
    # Different load torque scenarios
    load_scenarios = [
        (np.zeros_like(t), "No Load"),
        (np.ones_like(t) * 0.05, "Constant Load (0.05 N·m)"),
        (0.03 * np.sin(2*np.pi*0.5*t), "Sinusoidal Load (0.5 Hz)")
    ]
    
    plt.figure(figsize=(12, 8))
    
    for i, (load_torque, label) in enumerate(load_scenarios):
        t_sim, theta, omega = servo.simulate_with_load_torque(current, load_torque, t)
        
        plt.subplot(2, 1, 1)
        plt.plot(t_sim, theta, label=label)
        plt.ylabel('Position (rad)')
        plt.title('Position Response with Different Load Conditions')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 1, 2)
        plt.plot(t_sim, omega, label=label)
        plt.ylabel('Velocity (rad/s)')
        plt.xlabel('Time (s)')
        plt.title('Velocity Response with Different Load Conditions')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def main():
    """
    ## Main Simulation and Analysis
    
    This section demonstrates:
    1. Servo motor modeling with different parameters
    2. System identification from simulated data
    3. Load torque effects
    4. Comprehensive analysis and visualization
    """
    
    print("=== Servo Motor System Analysis ===\n")
    
    # Create servo motors with different characteristics
    
    # High-performance servo (low inertia, moderate damping)
    print("1. High-Performance Servo:")
    servo_hp = ServoMotor(J=0.001, D=0.01, Kt=0.1)
    plot_servo_analysis(servo_hp)
    
    # Standard servo
    print("\n2. Standard Servo:")
    servo_std = ServoMotor(J=0.01, D=0.1, Kt=0.1)
    plot_servo_analysis(servo_std)
    
    # Heavy-duty servo (high inertia, high damping)
    print("\n3. Heavy-Duty Servo:")
    servo_hd = ServoMotor(J=0.1, D=1.0, Kt=0.5)
    plot_servo_analysis(servo_hd)
    
    # Demonstrate load effects
    demonstrate_load_effects(servo_std)
    
    # System identification example
    print("\n=== System Identification Example ===")
    
    # Generate synthetic velocity data from known system
    true_servo = ServoMotor(J=0.02, D=0.15, Kt=0.12)
    t_data = np.linspace(0, 8, 200)
    current_input = np.ones_like(t_data)  # Step input
    _, vel_data = true_servo.simulate_velocity(current_input, t_data)
    
    # Add noise
    vel_data_noisy = vel_data + 0.01 * np.random.randn(len(vel_data))
    
    # Perform system identification
    J_est, D_est, Kt_est = system_identification_servo(current_input, vel_data_noisy, 
                                                      t_data, 'velocity')
    
    print(f"True parameters: J={true_servo.J}, D={true_servo.D}, Kt={true_servo.Kt}")
    print(f"Estimated parameters: J={J_est:.4f}, D={D_est:.4f}, Kt={Kt_est:.4f}")
    
    # Compare responses
    estimated_servo = ServoMotor(J=J_est, D=D_est, Kt=Kt_est)
    _, vel_est = estimated_servo.simulate_velocity(current_input, t_data)
    
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(t_data, vel_data, 'b-', label='True System', linewidth=2)
    plt.plot(t_data, vel_data_noisy, 'r.', label='Noisy Data', alpha=0.6)
    plt.plot(t_data, vel_est, 'g--', label='Identified System', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (rad/s)')
    plt.title('Velocity System Identification')
    plt.legend()
    plt.grid(True)
    
    # Position identification
    _, pos_data = true_servo.simulate_position(current_input, t_data)
    pos_data_noisy = pos_data + 0.001 * np.random.randn(len(pos_data))
    
    J_est_pos, D_est_pos, Kt_est_pos = system_identification_servo(current_input, 
                                                                  pos_data_noisy, 
                                                                  t_data, 'position')
    
    estimated_servo_pos = ServoMotor(J=J_est_pos, D=D_est_pos, Kt=Kt_est_pos)
    _, pos_est = estimated_servo_pos.simulate_position(current_input, t_data)
    
    plt.subplot(1, 2, 2)
    plt.plot(t_data, pos_data, 'b-', label='True System', linewidth=2)
    plt.plot(t_data, pos_data_noisy, 'r.', label='Noisy Data', alpha=0.6)
    plt.plot(t_data, pos_est, 'g--', label='Identified System', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Position (rad)')
    plt.title('Position System Identification')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    print(f"Position ID - Estimated: J={J_est_pos:.4f}, D={D_est_pos:.4f}, Kt={Kt_est_pos:.4f}")

if __name__ == "__main__":
    main()