"""
# Gearbox System

## Theory

A gearbox system with moment of inertia J, friction coefficient B, and input torque τ follows the equation:

$$J\ddot{\omega} + B\dot{\omega} = \tau$$

Where:
- $J$ is the moment of inertia (kg·m²)
- $B$ is the friction coefficient (N·m·s/rad)
- $\tau$ is the input torque (N·m)
- $\omega$ is the angular velocity (rad/s)

This is a first-order system. Taking the Laplace transform:

$$Js\Omega(s) + B\Omega(s) = \tau(s)$$

The transfer function from torque to angular velocity is:

$$G(s) = \frac{\Omega(s)}{\tau(s)} = \frac{1}{Js + B}$$

This can be rewritten as:

$$G(s) = \frac{K}{\tau s + 1}$$

Where:
- $K = 1/B$ is the DC gain (rad/s/N·m)
- $\tau = J/B$ is the time constant (s)

The system has a single pole at $s = -B/J$, making it stable.

For angular position output, the transfer function becomes:

$$G_\theta(s) = \frac{\Theta(s)}{\tau(s)} = \frac{1}{s(Js + B)}$$

This adds an integrator, making the system type 1 with zero steady-state error for step torque inputs.

## Gear Ratio Effects

For a gearbox with gear ratio $N = \omega_{in}/\omega_{out}$:
- Output torque: $\tau_{out} = N \cdot \tau_{in}$ (assuming 100% efficiency)
- Output speed: $\omega_{out} = \omega_{in}/N$
- Reflected inertia: $J_{reflected} = J_{load}/N^2$
- Reflected friction: $B_{reflected} = B_{load}/N^2$
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.optimize import curve_fit
import control as ct

class Gearbox:
    def __init__(self, J=0.01, B=0.1, gear_ratio=1.0, efficiency=0.95):
        """
        Initialize gearbox parameters
        
        Parameters:
        J (float): Moment of inertia (kg·m²)
        B (float): Friction coefficient (N·m·s/rad)
        gear_ratio (float): Gear ratio N = ω_in/ω_out (dimensionless)
        efficiency (float): Mechanical efficiency (0-1)
        """
        self.J = J
        self.B = B
        self.gear_ratio = gear_ratio
        self.efficiency = efficiency
        self.update_system()
    
    def update_system(self):
        """Update the system transfer function and state space representation"""
        # Transfer function from torque to angular velocity: G(s) = 1/(Js + B)
        num_vel = [1]
        den_vel = [self.J, self.B]
        self.tf_velocity = ct.TransferFunction(num_vel, den_vel)
        
        # Transfer function from torque to angular position: G(s) = 1/(s(Js + B))
        num_pos = [1]
        den_pos = [self.J, self.B, 0]
        self.tf_position = ct.TransferFunction(num_pos, den_pos)
        
        # State space representation: x1 = theta, x2 = omega
        # theta_dot = omega, omega_dot = (-B*omega + tau)/J
        A = [[0, 1], [0, -self.B/self.J]]
        B_matrix = [[0], [1/self.J]]
        C_pos = [[1, 0]]  # Position output
        C_vel = [[0, 1]]  # Velocity output
        D_matrix = [[0]]
        
        self.ss_position = ct.StateSpace(A, B_matrix, C_pos, D_matrix)
        self.ss_velocity = ct.StateSpace(A, B_matrix, C_vel, D_matrix)
        
        # System characteristics
        self.time_constant = self.J / self.B if self.B != 0 else float('inf')
        self.dc_gain_velocity = 1 / self.B if self.B != 0 else float('inf')
        
        # Gear ratio effects on output
        self.output_speed_gain = 1 / self.gear_ratio
        self.output_torque_gain = self.gear_ratio * self.efficiency
    
    def step_response_velocity(self, t_span=10, num_points=1000, output_side=False):
        """
        Generate step response for angular velocity
        
        Parameters:
        t_span (float): Time span for simulation
        num_points (int): Number of time points
        output_side (bool): If True, show output side velocity (divided by gear ratio)
        
        Returns:
        t (array): Time vector
        y (array): Velocity response vector
        """
        t = np.linspace(0, t_span, num_points)
        t, y = ct.step_response(self.tf_velocity, t)
        
        if output_side:
            y = y * self.output_speed_gain
        
        return t, y
    
    def step_response_position(self, t_span=10, num_points=1000, output_side=False):
        """Generate step response for angular position"""
        t = np.linspace(0, t_span, num_points)
        t, y = ct.step_response(self.tf_position, t)
        
        if output_side:
            y = y * self.output_speed_gain
        
        return t, y
    
    def impulse_response_velocity(self, t_span=10, num_points=1000, output_side=False):
        """Generate impulse response for angular velocity"""
        t = np.linspace(0, t_span, num_points)
        t, y = ct.impulse_response(self.tf_velocity, t)
        
        if output_side:
            y = y * self.output_speed_gain
        
        return t, y
    
    def impulse_response_position(self, t_span=10, num_points=1000, output_side=False):
        """Generate impulse response for angular position"""
        t = np.linspace(0, t_span, num_points)
        t, y = ct.impulse_response(self.tf_position, t)
        
        if output_side:
            y = y * self.output_speed_gain
        
        return t, y
    
    def frequency_response_velocity(self, freq_range=None, output_side=False):
        """
        Generate frequency response for angular velocity (Bode plot data)
        
        Parameters:
        freq_range (array): Frequency range in rad/s
        output_side (bool): If True, show output side response
        
        Returns:
        freq (array): Frequency vector
        mag (array): Magnitude response
        phase (array): Phase response
        """
        if freq_range is None:
            freq_range = np.logspace(-2, 2, 1000)
        
        freq, mag, phase = ct.bode(self.tf_velocity, freq_range, plot=False)
        
        if output_side:
            mag = mag * self.output_speed_gain
        
        return freq, mag, phase
    
    def frequency_response_position(self, freq_range=None, output_side=False):
        """Generate frequency response for angular position"""
        if freq_range is None:
            freq_range = np.logspace(-2, 2, 1000)
        
        freq, mag, phase = ct.bode(self.tf_position, freq_range, plot=False)
        
        if output_side:
            mag = mag * self.output_speed_gain
        
        return freq, mag, phase
    
    def simulate_velocity(self, torque_input, time, output_side=False):
        """
        Simulate angular velocity response to arbitrary torque input
        
        Parameters:
        torque_input (array): Input torque vector
        time (array): Time vector
        output_side (bool): If True, return output side velocity
        
        Returns:
        t (array): Time vector
        y (array): Velocity response
        """
        t, y = ct.forced_response(self.tf_velocity, time, torque_input)
        
        if output_side:
            y = y * self.output_speed_gain
        
        return t, y
    
    def simulate_position(self, torque_input, time, output_side=False):
        """Simulate angular position response to arbitrary torque input"""
        t, y = ct.forced_response(self.tf_position, time, torque_input)
        
        if output_side:
            y = y * self.output_speed_gain
        
        return t, y
    
    def simulate_with_load_torque(self, input_torque, load_torque, time, output_side=False):
        """
        Simulate system with both input torque and load torque
        
        ## Load Torque Effects
        
        With load torque $\tau_L$ reflected to the input side, the equation becomes:
        $$J\ddot{\omega} + B\dot{\omega} = \tau_{in} - \tau_L/N$$
        
        Where the load torque is reflected through the gear ratio.
        
        Parameters:
        input_torque (array): Input torque
        load_torque (array): Load torque (at output side)
        time (array): Time vector
        output_side (bool): If True, return output side quantities
        
        Returns:
        t (array): Time vector
        theta (array): Position response
        omega (array): Velocity response
        """
        # Reflect load torque to input side
        reflected_load = load_torque / (self.gear_ratio * self.efficiency)
        
        # Create augmented system with two inputs: input torque and reflected load torque
        A = [[0, 1], [0, -self.B/self.J]]
        B_matrix = [[0, 0], [1/self.J, -1/self.J]]  # Two inputs
        C = [[1, 0], [0, 1]]  # Both position and velocity outputs
        D_matrix = [[0, 0], [0, 0]]
        
        ss_dual = ct.StateSpace(A, B_matrix, C, D_matrix)
        
        # Combine inputs
        inputs = np.array([input_torque, reflected_load])
        
        t, y = ct.forced_response(ss_dual, time, inputs)
        theta = y[0]  # Position
        omega = y[1]  # Velocity
        
        if output_side:
            theta = theta * self.output_speed_gain
            omega = omega * self.output_speed_gain
        
        return t, theta, omega
    
    def simulate_with_backlash(self, torque_input, time, backlash_angle=0.01):
        """
        Simulate system with backlash nonlinearity
        
        ## Backlash Effects
        
        Backlash creates a dead zone in the gear train where input motion
        doesn't immediately translate to output motion. This is modeled as:
        
        - If |θ_error| < backlash_angle/2: τ_transmitted = 0
        - Else: τ_transmitted = τ_input
        
        Parameters:
        torque_input (array): Input torque
        time (array): Time vector
        backlash_angle (float): Total backlash angle (rad)
        
        Returns:
        t (array): Time vector
        theta_input (array): Input side position
        theta_output (array): Output side position with backlash
        """
        dt = time[1] - time[0]
        
        # Input side simulation (without backlash)
        _, theta_input = self.simulate_position(torque_input, time)
        omega_input = np.gradient(theta_input, dt)
        
        # Output side with backlash
        theta_output = np.zeros_like(time)
        omega_output = np.zeros_like(time)
        contact_state = 0  # -1: reverse contact, 0: no contact, 1: forward contact
        
        for i in range(1, len(time)):
            # Calculate error between input and output (accounting for gear ratio)
            theta_error = theta_input[i] / self.gear_ratio - theta_output[i-1]
            
            # Determine contact state
            if theta_error > backlash_angle/2:
                contact_state = 1  # Forward contact
            elif theta_error < -backlash_angle/2:
                contact_state = -1  # Reverse contact
            else:
                contact_state = 0  # No contact (in backlash zone)
            
            # Update output based on contact state
            if contact_state != 0:
                # In contact - output follows input
                omega_output[i] = omega_input[i] / self.gear_ratio
                theta_output[i] = theta_output[i-1] + omega_output[i] * dt
            else:
                # In backlash zone - output doesn't move
                omega_output[i] = 0
                theta_output[i] = theta_output[i-1]
        
        return time, theta_input, theta_output
    
    def calculate_gear_efficiency_loss(self, input_power, time):
        """
        Calculate power loss due to gear efficiency
        
        ## Efficiency Analysis
        
        Power loss in gears occurs due to:
        - Friction between gear teeth
        - Bearing losses
        - Oil churning losses
        
        Power_loss = (1 - efficiency) * Input_power
        
        Parameters:
        input_power (array): Input power (W)
        time (array): Time vector
        
        Returns:
        power_loss (array): Power dissipated as heat (W)
        output_power (array): Useful output power (W)
        """
        power_loss = (1 - self.efficiency) * np.abs(input_power)
        output_power = input_power * self.efficiency
        
        return power_loss, output_power

def system_identification_gearbox(input_data, output_data, time_data, output_type='velocity'):
    """
    Perform system identification to estimate J, B parameters
    
    ## System Identification for Gearboxes
    
    For velocity output, we fit a first-order system:
    $$G(s) = \frac{1}{Js + B} = \frac{K}{\tau s + 1}$$
    
    Where $K = 1/B$ is the DC gain and $\tau = J/B$ is the time constant.
    
    Parameters:
    input_data (array): Input torque data
    output_data (array): Output data (position or velocity)
    time_data (array): Time vector
    output_type (str): 'velocity' or 'position'
    
    Returns:
    J_est, B_est: Estimated parameters
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
                # K = 1/B, tau = J/B
                B_est = 1 / K_est
                J_est = tau_est * B_est
                
            except:
                # Fallback values
                J_est, B_est = 0.01, 0.1
        else:
            # For non-step inputs, use more complex identification
            J_est, B_est = 0.01, 0.1
    
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
                J_est = tau_est * B_est
                
            except:
                J_est, B_est = 0.01, 0.1
        else:
            J_est, B_est = 0.01, 0.1
    
    return J_est, B_est

def plot_gearbox_analysis(gearbox, save_plots=False):
    """
    Generate comprehensive plots for gearbox analysis
    
    Parameters:
    gearbox (Gearbox): System to analyze
    save_plots (bool): Whether to save plots to files
    """
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    title = f'Gearbox Analysis (J={gearbox.J}, B={gearbox.B}, N={gearbox.gear_ratio}, η={gearbox.efficiency})'
    fig.suptitle(title, fontsize=14)
    
    # Velocity step response (input and output sides)
    t_vel_in, y_vel_in = gearbox.step_response_velocity(output_side=False)
    t_vel_out, y_vel_out = gearbox.step_response_velocity(output_side=True)
    
    axes[0,0].plot(t_vel_in, y_vel_in, 'b-', label='Input Side')
    axes[0,0].plot(t_vel_out, y_vel_out, 'r--', label='Output Side')
    axes[0,0].set_title('Velocity Step Response')
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Velocity (rad/s)')
    axes[0,0].legend()
    axes[0,0].grid(True)
    
    # Position step response
    t_pos_in, y_pos_in = gearbox.step_response_position(output_side=False)
    t_pos_out, y_pos_out = gearbox.step_response_position(output_side=True)
    
    axes[0,1].plot(t_pos_in, y_pos_in, 'b-', label='Input Side')
    axes[0,1].plot(t_pos_out, y_pos_out, 'r--', label='Output Side')
    axes[0,1].set_title('Position Step Response')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Position (rad)')
    axes[0,1].legend()
    axes[0,1].grid(True)
    
    # Velocity frequency response
    freq_vel_in, mag_vel_in, phase_vel_in = gearbox.frequency_response_velocity(output_side=False)
    freq_vel_out, mag_vel_out, phase_vel_out = gearbox.frequency_response_velocity(output_side=True)
    
    axes[1,0].loglog(freq_vel_in, np.abs(mag_vel_in), 'b-', label='Input Side')
    axes[1,0].loglog(freq_vel_out, np.abs(mag_vel_out), 'r--', label='Output Side')
    axes[1,0].set_title('Velocity Bode - Magnitude')
    axes[1,0].set_xlabel('Frequency (rad/s)')
    axes[1,0].set_ylabel('Magnitude')
    axes[1,0].legend()
    axes[1,0].grid(True)
    
    # Position frequency response
    freq_pos_in, mag_pos_in, phase_pos_in = gearbox.frequency_response_position(output_side=False)
    freq_pos_out, mag_pos_out, phase_pos_out = gearbox.frequency_response_position(output_side=True)
    
    axes[1,1].loglog(freq_pos_in, np.abs(mag_pos_in), 'b-', label='Input Side')
    axes[1,1].loglog(freq_pos_out, np.abs(mag_pos_out), 'r--', label='Output Side')
    axes[1,1].set_title('Position Bode - Magnitude')
    axes[1,1].set_xlabel('Frequency (rad/s)')
    axes[1,1].set_ylabel('Magnitude')
    axes[1,1].legend()
    axes[1,1].grid(True)
    
    # Phase plots
    axes[2,0].semilogx(freq_vel_in, np.angle(mag_vel_in)*180/np.pi, 'b-', label='Input Side')
    axes[2,0].semilogx(freq_vel_out, np.angle(mag_vel_out)*180/np.pi, 'r--', label='Output Side')
    axes[2,0].set_title('Velocity Bode - Phase')
    axes[2,0].set_xlabel('Frequency (rad/s)')
    axes[2,0].set_ylabel('Phase (degrees)')
    axes[2,0].legend()
    axes[2,0].grid(True)
    
    axes[2,1].semilogx(freq_pos_in, np.angle(mag_pos_in)*180/np.pi, 'b-', label='Input Side')
    axes[2,1].semilogx(freq_pos_out, np.angle(mag_pos_out)*180/np.pi, 'r--', label='Output Side')
    axes[2,1].set_title('Position Bode - Phase')
    axes[2,1].set_xlabel('Frequency (rad/s)')
    axes[2,1].set_ylabel('Phase (degrees)')
    axes[2,1].legend()
    axes[2,1].grid(True)
    
    plt.tight_layout()
    
    if save_plots:
        plt.savefig('gearbox_analysis.png', dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Print system characteristics
    print(f"System Characteristics:")
    print(f"Time constant (τ): {gearbox.time_constant:.3f} s")
    print(f"DC gain (input side): {gearbox.dc_gain_velocity:.3f} rad/s/N·m")
    print(f"Speed reduction ratio: {gearbox.gear_ratio:.1f}:1")
    print(f"Torque amplification: {gearbox.output_torque_gain:.1f}x")
    print(f"Bandwidth (-3dB): {1/gearbox.time_constant:.3f} rad/s")

def demonstrate_gear_ratio_effects():
    """
    Demonstrate the effect of different gear ratios
    
    ## Gear Ratio Analysis
    
    Different gear ratios affect:
    - Speed reduction: ω_out = ω_in / N
    - Torque amplification: τ_out = τ_in × N × η
    - System dynamics remain the same on input side
    """
    
    print("\n=== Gear Ratio Effects ===")
    
    # Fixed J and B, vary gear ratio
    J, B = 0.02, 0.15
    
    gear_ratios = [1, 5, 10, 25]  # Different reduction ratios
    
    plt.figure(figsize=(15, 10))
    
    for i, N in enumerate(gear_ratios):
        gearbox = Gearbox(J=J, B=B, gear_ratio=N)
        
        # Step response comparison
        t, vel_in = gearbox.step_response_velocity(output_side=False)
        t, vel_out = gearbox.step_response_velocity(output_side=True)
        
        plt.subplot(2, 2, 1)
        plt.plot(t, vel_in, label=f'Input Side (N={N}:1)')
        plt.ylabel('Input Velocity (rad/s)')
        plt.title('Input Side Velocity (Same for all ratios)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 2)
        plt.plot(t, vel_out, label=f'N={N}:1')
        plt.ylabel('Output Velocity (rad/s)')
        plt.title('Output Side Velocity (Speed Reduction)')
        plt.xlabel('Time (s)')
        plt.legend()
        plt.grid(True)
        
        # Frequency response
        freq, mag_in, _ = gearbox.frequency_response_velocity(output_side=False)
        freq, mag_out, _ = gearbox.frequency_response_velocity(output_side=True)
        
        plt.subplot(2, 2, 3)
        plt.loglog(freq, np.abs(mag_in), label=f'Input Side (N={N}:1)')
        plt.ylabel('Input Magnitude')
        plt.title('Input Side Frequency Response')
        plt.xlabel('Frequency (rad/s)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 4)
        plt.loglog(freq, np.abs(mag_out), label=f'N={N}:1')
        plt.ylabel('Output Magnitude')
        plt.title('Output Side Frequency Response')
        plt.xlabel('Frequency (rad/s)')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def demonstrate_load_effects(gearbox):
    """
    Demonstrate the effect of load torques on gearbox performance
    
    ## Load Torque Analysis
    
    Load torques on the output side are reflected to the input side:
    - Reflected load = Load_torque / (N × η)
    - This affects input side dynamics
    """
    
    print("\n=== Load Torque Effects ===")
    
    t = np.linspace(0, 15, 1000)
    input_torque = np.ones_like(t) * 2.0  # 2 N·m step input torque
    
    # Different load torque scenarios (at output side)
    load_scenarios = [
        (np.zeros_like(t), "No Load"),
        (np.ones_like(t) * 5.0, "Constant Load (5 N·m)"),
        (3.0 * np.sin(2*np.pi*0.1*t), "Sinusoidal Load (0.1 Hz)"),
        (8.0 * (t > 8) * (t < 10), "Step Load (8-10s)")
    ]
    
    plt.figure(figsize=(15, 12))
    
    for i, (load_torque, label) in enumerate(load_scenarios):
        t_sim, theta_in, omega_in = gearbox.simulate_with_load_torque(input_torque, load_torque, t, output_side=False)
        t_sim, theta_out, omega_out = gearbox.simulate_with_load_torque(input_torque, load_torque, t, output_side=True)
        
        plt.subplot(3, 2, 1)
        plt.plot(t_sim, load_torque, label=label)
        plt.ylabel('Load Torque (N·m)')
        plt.title('Load Torque at Output Side')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 2, 2)
        plt.plot(t_sim, load_torque / (gearbox.gear_ratio * gearbox.efficiency), label=label)
        plt.ylabel('Reflected Load (N·m)')
        plt.title('Load Torque Reflected to Input Side')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 2, 3)
        plt.plot(t_sim, omega_in, label=label)
        plt.ylabel('Input Velocity (rad/s)')
        plt.title('Input Side Velocity Response')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 2, 4)
        plt.plot(t_sim, omega_out, label=label)
        plt.ylabel('Output Velocity (rad/s)')
        plt.title('Output Side Velocity Response')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 2, 5)
        plt.plot(t_sim, theta_in, label=label)
        plt.ylabel('Input Position (rad)')
        plt.xlabel('Time (s)')
        plt.title('Input Side Position Response')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 2, 6)
        plt.plot(t_sim, theta_out, label=label)
        plt.ylabel('Output Position (rad)')
        plt.xlabel('Time (s)')
        plt.title('Output Side Position Response')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def demonstrate_backlash_effects(gearbox):
    """
    Demonstrate the effect of backlash on gearbox performance
    
    ## Backlash Analysis
    
    Backlash creates dead zones where input motion doesn't immediately
    translate to output motion. This causes:
    - Lost motion
    - Positioning errors
    - Oscillations in closed-loop systems
    """
    
    print("\n=== Backlash Effects ===")
    
    t = np.linspace(0, 20, 2000)
    
    # Different input scenarios
    input_scenarios = [
        (2.0 * np.sin(2*np.pi*0.1*t), "Sinusoidal Input (0.1 Hz)"),
        (1.0 * signal.square(2*np.pi*0.05*t), "Square Wave Input"),
        (0.5 * t * (t < 10) - 0.5 * 10 * (t >= 10), "Triangular Input")
    ]
    
    backlash_angles = [0, 0.02, 0.05]  # Different backlash amounts
    
    for input_torque, input_label in input_scenarios:
        plt.figure(figsize=(15, 10))
        
        for i, backlash in enumerate(backlash_angles):
            t_sim, theta_in, theta_out = gearbox.simulate_with_backlash(input_torque, t, backlash)
            
            plt.subplot(3, 1, 1)
            plt.plot(t_sim, input_torque, 'k-', alpha=0.7)
            plt.ylabel('Input Torque (N·m)')
            plt.title(f'{input_label} - Input Torque')
            plt.grid(True)
            
            plt.subplot(3, 1, 2)
            plt.plot(t_sim, theta_in / gearbox.gear_ratio, label=f'Ideal Output (Backlash={backlash:.3f} rad)')
            plt.ylabel('Output Position (rad)')
            plt.title('Ideal Output Position (No Backlash)')
            plt.legend()
            plt.grid(True)
            
            plt.subplot(3, 1, 3)
            plt.plot(t_sim, theta_out, label=f'Backlash={backlash:.3f} rad')
            plt.ylabel('Actual Output (rad)')
            plt.xlabel('Time (s)')
            plt.title('Actual Output Position (With Backlash)')
            plt.legend()
            plt.grid(True)
        
        plt.tight_layout()
        plt.show()

def main():
    """
    ## Main Simulation and Analysis
    
    This section demonstrates:
    1. Gearbox modeling with different parameters
    2. Gear ratio effects on system behavior
    3. Load torque effects
    4. Backlash nonlinearity effects
    5. System identification from simulated data
    6. Comprehensive analysis and visualization
    """
    
    print("=== Gearbox System Analysis ===\n")
    
    # Create gearboxes with different characteristics
    
    # Direct drive (no gear reduction)
    print("1. Direct Drive (1:1 ratio):")
    gearbox_direct = Gearbox(J=0.005, B=0.05, gear_ratio=1.0)
    plot_gearbox_analysis(gearbox_direct)
    
    # Medium reduction gearbox
    print("\n2. Medium Reduction Gearbox (10:1):")
    gearbox_medium = Gearbox(J=0.02, B=0.1, gear_ratio=10.0)
    plot_gearbox_analysis(gearbox_medium)
    
    # High reduction gearbox
    print("\n3. High Reduction Gearbox (50:1):")
    gearbox_high = Gearbox(J=0.05, B=0.2, gear_ratio=50.0, efficiency=0.85)
    plot_gearbox_analysis(gearbox_high)
    
    # Demonstrate gear ratio effects
    demonstrate_gear_ratio_effects()
    
    # Demonstrate load effects
    demonstrate_load_effects(gearbox_medium)
    
    # Demonstrate backlash effects
    demonstrate_backlash_effects(gearbox_medium)
    
    # Efficiency analysis
    print("\n=== Efficiency Analysis ===")
    
    t = np.linspace(0, 10, 1000)
    input_torque = 3.0 * np.sin(2*np.pi*0.2*t)  # Sinusoidal torque
    input_velocity = 10.0 * np.cos(2*np.pi*0.2*t)  # Corresponding velocity
    input_power = input_torque * input_velocity
    
    power_loss, output_power = gearbox_medium.calculate_gear_efficiency_loss(input_power, t)
    
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(t, input_torque)
    plt.ylabel('Torque (N·m)')
    plt.title('Input Torque')
    plt.grid(True)
    
    plt.subplot(2, 2, 2)
    plt.plot(t, input_velocity)
    plt.ylabel('Velocity (rad/s)')
    plt.title('Input Velocity')
    plt.grid(True)
    
    plt.subplot(2, 2, 3)
    plt.plot(t, input_power, 'b-', label='Input Power')
    plt.plot(t, output_power, 'g-', label='Output Power')
    plt.plot(t, power_loss, 'r-', label='Power Loss')
    plt.ylabel('Power (W)')
    plt.xlabel('Time (s)')
    plt.title('Power Analysis')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 2, 4)
    efficiency_actual = np.abs(output_power) / (np.abs(input_power) + 1e-10)  # Avoid division by zero
    plt.plot(t, efficiency_actual * 100)
    plt.axhline(y=gearbox_medium.efficiency * 100, color='r', linestyle='--', label='Nominal Efficiency')
    plt.ylabel('Efficiency (%)')
    plt.xlabel('Time (s)')
    plt.title('Instantaneous Efficiency')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    total_energy_in = np.trapz(np.abs(input_power), t)
    total_energy_out = np.trapz(np.abs(output_power), t)
    total_energy_loss = np.trapz(power_loss, t)
    
    print(f"Energy Analysis:")
    print(f"Total input energy: {total_energy_in:.2f} J")
    print(f"Total output energy: {total_energy_out:.2f} J")
    print(f"Total energy loss: {total_energy_loss:.2f} J")
    print(f"Overall efficiency: {(total_energy_out/total_energy_in)*100:.1f}%")
    
    # System identification example
    print("\n=== System Identification Example ===")
    
    # Generate synthetic velocity data from known system
    true_gearbox = Gearbox(J=0.025, B=0.12)
    t_data = np.linspace(0, 8, 200)
    torque_input = np.ones_like(t_data) * 1.5  # Step input
    _, vel_data = true_gearbox.simulate_velocity(torque_input, t_data)
    
    # Add noise
    vel_data_noisy = vel_data + 0.05 * np.random.randn(len(vel_data))
    
    # Perform system identification
    J_est, B_est = system_identification_gearbox(torque_input, vel_data_noisy, 
                                                t_data, 'velocity')
    
    print(f"True parameters: J={true_gearbox.J}, B={true_gearbox.B}")
    print(f"Estimated parameters: J={J_est:.4f}, B={B_est:.4f}")
    
    # Compare responses
    estimated_gearbox = Gearbox(J=J_est, B=B_est)
    _, vel_est = estimated_gearbox.simulate_velocity(torque_input, t_data)
    
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
    _, pos_data = true_gearbox.simulate_position(torque_input, t_data)
    pos_data_noisy = pos_data + 0.002 * np.random.randn(len(pos_data))
    
    J_est_pos, B_est_pos = system_identification_gearbox(torque_input, 
                                                        pos_data_noisy, 
                                                        t_data, 'position')
    
    estimated_gearbox_pos = Gearbox(J=J_est_pos, B=B_est_pos)
    _, pos_est = estimated_gearbox_pos.simulate_position(torque_input, t_data)
    
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
    
    print(f"Position ID - Estimated: J={J_est_pos:.4f}, B={B_est_pos:.4f}")

if __name__ == "__main__":
    main()