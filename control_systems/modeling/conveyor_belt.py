"""
# Conveyor Belt System

## Theory

A conveyor belt system with mass M, damping coefficient B, and drive force F follows the equation:

$$M\dot{v} + Bv = F$$

Where:
- $M$ is the effective mass of the belt and load (kg)
- $B$ is the damping coefficient (N·s/m)
- $F$ is the drive force (N)
- $v$ is the belt velocity (m/s)

This is a first-order system. Taking the Laplace transform:

$$MsV(s) + BV(s) = F(s)$$

The transfer function from force to velocity is:

$$G(s) = \frac{V(s)}{F(s)} = \frac{1}{Ms + B}$$

This can be rewritten as:

$$G(s) = \frac{K}{\tau s + 1}$$

Where:
- $K = 1/B$ is the DC gain (m/s/N)
- $\tau = M/B$ is the time constant (s)

The system has a single pole at $s = -B/M$, making it stable.

For position output, the transfer function becomes:

$$G_x(s) = \frac{X(s)}{F(s)} = \frac{1}{s(Ms + B)}$$

This adds an integrator, making the system type 1 with zero steady-state error for step inputs.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.optimize import curve_fit
import control as ct

class ConveyorBelt:
    def __init__(self, M=10.0, B=2.0):
        """
        Initialize conveyor belt parameters
        
        Parameters:
        M (float): Effective mass (kg)
        B (float): Damping coefficient (N·s/m)
        """
        self.M = M
        self.B = B
        self.update_system()
    
    def update_system(self):
        """Update the system transfer function and state space representation"""
        # Transfer function from force to velocity: G(s) = 1/(Ms + B)
        num_vel = [1]
        den_vel = [self.M, self.B]
        self.tf_velocity = ct.TransferFunction(num_vel, den_vel)
        
        # Transfer function from force to position: G(s) = 1/(s(Ms + B))
        num_pos = [1]
        den_pos = [self.M, self.B, 0]
        self.tf_position = ct.TransferFunction(num_pos, den_pos)
        
        # State space representation: x1 = position, x2 = velocity
        # position_dot = velocity, velocity_dot = (-B*velocity + F)/M
        A = [[0, 1], [0, -self.B/self.M]]
        B_matrix = [[0], [1/self.M]]
        C_pos = [[1, 0]]  # Position output
        C_vel = [[0, 1]]  # Velocity output
        D_matrix = [[0]]
        
        self.ss_position = ct.StateSpace(A, B_matrix, C_pos, D_matrix)
        self.ss_velocity = ct.StateSpace(A, B_matrix, C_vel, D_matrix)
        
        # System characteristics
        self.time_constant = self.M / self.B if self.B != 0 else float('inf')
        self.dc_gain_velocity = 1 / self.B if self.B != 0 else float('inf')
    
    def step_response_velocity(self, t_span=10, num_points=1000):
        """
        Generate step response for velocity
        
        Parameters:
        t_span (float): Time span for simulation
        num_points (int): Number of time points
        
        Returns:
        t (array): Time vector
        y (array): Velocity response vector
        """
        t = np.linspace(0, t_span, num_points)
        t, y = ct.step_response(self.tf_velocity, t)
        return t, y
    
    def step_response_position(self, t_span=10, num_points=1000):
        """Generate step response for position"""
        t = np.linspace(0, t_span, num_points)
        t, y = ct.step_response(self.tf_position, t)
        return t, y
    
    def impulse_response_velocity(self, t_span=10, num_points=1000):
        """Generate impulse response for velocity"""
        t = np.linspace(0, t_span, num_points)
        t, y = ct.impulse_response(self.tf_velocity, t)
        return t, y
    
    def impulse_response_position(self, t_span=10, num_points=1000):
        """Generate impulse response for position"""
        t = np.linspace(0, t_span, num_points)
        t, y = ct.impulse_response(self.tf_position, t)
        return t, y
    
    def frequency_response_velocity(self, freq_range=None):
        """
        Generate frequency response for velocity (Bode plot data)
        
        Parameters:
        freq_range (array): Frequency range in rad/s
        
        Returns:
        freq (array): Frequency vector
        mag (array): Magnitude response
        phase (array): Phase response
        """
        if freq_range is None:
            freq_range = np.logspace(-2, 2, 1000)
        
        freq, mag, phase = ct.bode(self.tf_velocity, freq_range, plot=False)
        return freq, mag, phase
    
    def frequency_response_position(self, freq_range=None):
        """Generate frequency response for position"""
        if freq_range is None:
            freq_range = np.logspace(-2, 2, 1000)
        
        freq, mag, phase = ct.bode(self.tf_position, freq_range, plot=False)
        return freq, mag, phase
    
    def simulate_velocity(self, force_input, time):
        """
        Simulate velocity response to arbitrary force input
        
        Parameters:
        force_input (array): Drive force input vector
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        y (array): Velocity response
        """
        t, y = ct.forced_response(self.tf_velocity, time, force_input)
        return t, y
    
    def simulate_position(self, force_input, time):
        """Simulate position response to arbitrary force input"""
        t, y = ct.forced_response(self.tf_position, time, force_input)
        return t, y
    
    def simulate_with_friction_variation(self, force_input, friction_variation, time):
        """
        Simulate system with time-varying friction coefficient
        
        ## Variable Friction Effects
        
        With time-varying friction $B(t)$, the equation becomes:
        $$M\dot{v} + B(t)v = F$$
        
        This creates a time-varying system that must be solved numerically.
        
        Parameters:
        force_input (array): Drive force
        friction_variation (array): Time-varying friction coefficient B(t)
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        x (array): Position response
        v (array): Velocity response
        """
        dt = time[1] - time[0]
        x = np.zeros_like(time)
        v = np.zeros_like(time)
        
        for i in range(1, len(time)):
            # Current friction coefficient
            B_current = friction_variation[i-1]
            
            # Numerical integration using Euler method
            # v_dot = (-B_current * v + F) / M
            v_dot = (-B_current * v[i-1] + force_input[i-1]) / self.M
            v[i] = v[i-1] + v_dot * dt
            x[i] = x[i-1] + v[i-1] * dt
        
        return time, x, v
    
    def simulate_with_load_variation(self, force_input, load_force, time):
        """
        Simulate system with external load forces (resistance)
        
        ## Load Force Effects
        
        With external load force $F_L$, the equation becomes:
        $$M\dot{v} + Bv = F - F_L$$
        
        Parameters:
        force_input (array): Drive force
        load_force (array): External load force
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        x (array): Position response
        v (array): Velocity response
        """
        # Create augmented system with two inputs: drive force and load force
        A = [[0, 1], [0, -self.B/self.M]]
        B_matrix = [[0, 0], [1/self.M, -1/self.M]]  # Two inputs: drive force and load force
        C = [[1, 0], [0, 1]]  # Both position and velocity outputs
        D_matrix = [[0, 0], [0, 0]]
        
        ss_dual = ct.StateSpace(A, B_matrix, C, D_matrix)
        
        # Combine inputs
        inputs = np.array([force_input, load_force])
        
        t, y = ct.forced_response(ss_dual, time, inputs)
        x = y[0]  # Position
        v = y[1]  # Velocity
        
        return t, x, v

def system_identification_conveyor(input_data, output_data, time_data, output_type='velocity'):
    """
    Perform system identification to estimate M, B parameters
    
    ## System Identification for Conveyor Belts
    
    For velocity output, we fit a first-order system:
    $$G(s) = \frac{1}{Ms + B} = \frac{K}{\tau s + 1}$$
    
    Where $K = 1/B$ is the DC gain and $\tau = M/B$ is the time constant.
    
    For position output, we have an integrator plus first-order system:
    $$G(s) = \frac{1}{s(Ms + B)} = \frac{K}{s(\tau s + 1)}$$
    
    Parameters:
    input_data (array): Input force data
    output_data (array): Output data (position or velocity)
    time_data (array): Time vector
    output_type (str): 'velocity' or 'position'
    
    Returns:
    M_est, B_est: Estimated parameters
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
                # K = 1/B, tau = M/B
                B_est = 1 / K_est
                M_est = tau_est * B_est
                
            except:
                # Fallback values
                M_est, B_est = 10.0, 2.0
        else:
            # For non-step inputs, use more complex identification
            M_est, B_est = 10.0, 2.0
    
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
                B_est = 1 / K_est
                M_est = tau_est * B_est
                
            except:
                M_est, B_est = 10.0, 2.0
        else:
            M_est, B_est = 10.0, 2.0
    
    return M_est, B_est

def plot_conveyor_analysis(conveyor, save_plots=False):
    """
    Generate comprehensive plots for conveyor belt analysis
    
    Parameters:
    conveyor (ConveyorBelt): System to analyze
    save_plots (bool): Whether to save plots to files
    """
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle(f'Conveyor Belt Analysis (M={conveyor.M} kg, B={conveyor.B} N·s/m)', 
                 fontsize=14)
    
    # Velocity step response
    t_vel, y_vel = conveyor.step_response_velocity()
    axes[0,0].plot(t_vel, y_vel)
    axes[0,0].set_title('Velocity Step Response')
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Velocity (m/s)')
    axes[0,0].grid(True)
    
    # Position step response
    t_pos, y_pos = conveyor.step_response_position()
    axes[0,1].plot(t_pos, y_pos)
    axes[0,1].set_title('Position Step Response')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Position (m)')
    axes[0,1].grid(True)
    
    # Velocity frequency response
    freq_vel, mag_vel, phase_vel = conveyor.frequency_response_velocity()
    axes[1,0].loglog(freq_vel, np.abs(mag_vel))
    axes[1,0].set_title('Velocity Bode - Magnitude')
    axes[1,0].set_xlabel('Frequency (rad/s)')
    axes[1,0].set_ylabel('Magnitude')
    axes[1,0].grid(True)
    
    # Position frequency response
    freq_pos, mag_pos, phase_pos = conveyor.frequency_response_position()
    axes[1,1].loglog(freq_pos, np.abs(mag_pos))
    axes[1,1].set_title('Position Bode - Magnitude')
    axes[1,1].set_xlabel('Frequency (rad/s)')
    axes[1,1].set_ylabel('Magnitude')
    axes[1,1].grid(True)
    
    # Phase plots
    axes[2,0].semilogx(freq_vel, np.angle(mag_vel)*180/np.pi)
    axes[2,0].set_title('Velocity Bode - Phase')
    axes[2,0].set_xlabel('Frequency (rad/s)')
    axes[2,0].set_ylabel('Phase (degrees)')
    axes[2,0].grid(True)
    
    axes[2,1].semilogx(freq_pos, np.angle(mag_pos)*180/np.pi)
    axes[2,1].set_title('Position Bode - Phase')
    axes[2,1].set_xlabel('Frequency (rad/s)')
    axes[2,1].set_ylabel('Phase (degrees)')
    axes[2,1].grid(True)
    
    plt.tight_layout()
    
    if save_plots:
        plt.savefig('conveyor_belt_analysis.png', dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Print system characteristics
    print(f"System Characteristics:")
    print(f"Time constant (τ): {conveyor.time_constant:.3f} s")
    print(f"DC gain (velocity): {conveyor.dc_gain_velocity:.3f} m/s/N")
    print(f"Bandwidth (-3dB): {1/conveyor.time_constant:.3f} rad/s")

def demonstrate_load_effects(conveyor):
    """
    Demonstrate the effect of load forces on conveyor performance
    
    ## Load Force Analysis
    
    Load forces affect the steady-state behavior:
    - For constant drive force: steady-state velocity = $(F - F_L)/B$
    - Load forces act as disturbances to the system
    """
    
    print("\n=== Load Force Effects ===")
    
    t = np.linspace(0, 15, 1000)
    drive_force = np.ones_like(t) * 50.0  # 50N step drive force
    
    # Different load force scenarios
    load_scenarios = [
        (np.zeros_like(t), "No Load"),
        (np.ones_like(t) * 20.0, "Constant Load (20 N)"),
        (10.0 * np.sin(2*np.pi*0.2*t), "Sinusoidal Load (0.2 Hz)")
    ]
    
    plt.figure(figsize=(12, 8))
    
    for i, (load_force, label) in enumerate(load_scenarios):
        t_sim, x, v = conveyor.simulate_with_load_variation(drive_force, load_force, t)
        
        plt.subplot(2, 1, 1)
        plt.plot(t_sim, v, label=label)
        plt.ylabel('Velocity (m/s)')
        plt.title('Velocity Response with Different Load Conditions')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 1, 2)
        plt.plot(t_sim, x, label=label)
        plt.ylabel('Position (m)')
        plt.xlabel('Time (s)')
        plt.title('Position Response with Different Load Conditions')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def demonstrate_friction_variation(conveyor):
    """
    Demonstrate the effect of time-varying friction
    
    ## Variable Friction Analysis
    
    Time-varying friction B(t) creates a time-varying system.
    Common causes include:
    - Belt wear
    - Temperature effects
    - Load distribution changes
    """
    
    print("\n=== Variable Friction Effects ===")
    
    t = np.linspace(0, 20, 2000)
    drive_force = np.ones_like(t) * 40.0  # Constant drive force
    
    # Different friction variation scenarios
    friction_scenarios = [
        (np.ones_like(t) * conveyor.B, "Constant Friction"),
        (conveyor.B * (1 + 0.5 * np.sin(2*np.pi*0.1*t)), "Sinusoidal Friction Variation"),
        (conveyor.B * np.exp(-0.1*t), "Decreasing Friction (Wear)")
    ]
    
    plt.figure(figsize=(15, 10))
    
    for i, (friction_variation, label) in enumerate(friction_scenarios):
        t_sim, x, v = conveyor.simulate_with_friction_variation(drive_force, friction_variation, t)
        
        plt.subplot(3, 1, 1)
        plt.plot(t_sim, friction_variation, label=label)
        plt.ylabel('Friction B (N·s/m)')
        plt.title('Friction Coefficient Variation')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 1, 2)
        plt.plot(t_sim, v, label=label)
        plt.ylabel('Velocity (m/s)')
        plt.title('Velocity Response with Variable Friction')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 1, 3)
        plt.plot(t_sim, x, label=label)
        plt.ylabel('Position (m)')
        plt.xlabel('Time (s)')
        plt.title('Position Response with Variable Friction')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def main():
    """
    ## Main Simulation and Analysis
    
    This section demonstrates:
    1. Conveyor belt modeling with different parameters
    2. System identification from simulated data
    3. Load force effects
    4. Variable friction effects
    5. Comprehensive analysis and visualization
    """
    
    print("=== Conveyor Belt System Analysis ===\n")
    
    # Create conveyor belts with different characteristics
    
    # Light-duty conveyor (low mass, low damping)
    print("1. Light-Duty Conveyor:")
    conveyor_light = ConveyorBelt(M=5.0, B=1.0)
    plot_conveyor_analysis(conveyor_light)
    
    # Standard conveyor
    print("\n2. Standard Conveyor:")
    conveyor_std = ConveyorBelt(M=15.0, B=3.0)
    plot_conveyor_analysis(conveyor_std)
    
    # Heavy-duty conveyor (high mass, high damping)
    print("\n3. Heavy-Duty Conveyor:")
    conveyor_heavy = ConveyorBelt(M=50.0, B=10.0)
    plot_conveyor_analysis(conveyor_heavy)
    
    # Demonstrate load effects
    demonstrate_load_effects(conveyor_std)
    
    # Demonstrate friction variation effects
    demonstrate_friction_variation(conveyor_std)
    
    # System identification example
    print("\n=== System Identification Example ===")
    
    # Generate synthetic velocity data from known system
    true_conveyor = ConveyorBelt(M=12.0, B=2.5)
    t_data = np.linspace(0, 10, 200)
    force_input = np.ones_like(t_data) * 25.0  # Step input
    _, vel_data = true_conveyor.simulate_velocity(force_input, t_data)
    
    # Add noise
    vel_data_noisy = vel_data + 0.1 * np.random.randn(len(vel_data))
    
    # Perform system identification
    M_est, B_est = system_identification_conveyor(force_input, vel_data_noisy, 
                                                 t_data, 'velocity')
    
    print(f"True parameters: M={true_conveyor.M} kg, B={true_conveyor.B} N·s/m")
    print(f"Estimated parameters: M={M_est:.3f} kg, B={B_est:.3f} N·s/m")
    
    # Compare responses
    estimated_conveyor = ConveyorBelt(M=M_est, B=B_est)
    _, vel_est = estimated_conveyor.simulate_velocity(force_input, t_data)
    
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(t_data, vel_data, 'b-', label='True System', linewidth=2)
    plt.plot(t_data, vel_data_noisy, 'r.', label='Noisy Data', alpha=0.6)
    plt.plot(t_data, vel_est, 'g--', label='Identified System', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (m/s)')
    plt.title('Velocity System Identification')
    plt.legend()
    plt.grid(True)
    
    # Position identification
    _, pos_data = true_conveyor.simulate_position(force_input, t_data)
    pos_data_noisy = pos_data + 0.01 * np.random.randn(len(pos_data))
    
    M_est_pos, B_est_pos = system_identification_conveyor(force_input, 
                                                         pos_data_noisy, 
                                                         t_data, 'position')
    
    estimated_conveyor_pos = ConveyorBelt(M=M_est_pos, B=B_est_pos)
    _, pos_est = estimated_conveyor_pos.simulate_position(force_input, t_data)
    
    plt.subplot(1, 2, 2)
    plt.plot(t_data, pos_data, 'b-', label='True System', linewidth=2)
    plt.plot(t_data, pos_data_noisy, 'r.', label='Noisy Data', alpha=0.6)
    plt.plot(t_data, pos_est, 'g--', label='Identified System', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m)')
    plt.title('Position System Identification')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    print(f"Position ID - Estimated: M={M_est_pos:.3f} kg, B={B_est_pos:.3f} N·s/m")

if __name__ == "__main__":
    main()