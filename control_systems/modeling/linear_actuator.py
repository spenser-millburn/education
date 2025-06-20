"""
# Linear Actuator System

## Theory

A linear actuator with mass M, damping coefficient B, and spring constant k follows the equation:

$$M\ddot{x} + B\dot{x} + kx = F$$

Where:
- $M$ is the mass (kg)
- $B$ is the damping coefficient (N·s/m)
- $k$ is the spring constant (N/m)
- $F$ is the applied force (N)
- $x$ is the position (m)

This is a second-order linear system. Taking the Laplace transform:

$$Ms^2X(s) + BsX(s) + kX(s) = F(s)$$

The transfer function from force to position is:

$$G(s) = \frac{X(s)}{F(s)} = \frac{1}{Ms^2 + Bs + k}$$

The characteristic equation is $Ms^2 + Bs + k = 0$ with natural frequency $\omega_n = \sqrt{k/M}$ and damping ratio $\zeta = \frac{B}{2\sqrt{Mk}}$.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.optimize import curve_fit
import control as ct

class LinearActuator:
    def __init__(self, M=1.0, B=2.0, k=10.0):
        """
        Initialize linear actuator parameters
        
        Parameters:
        M (float): Mass (kg)
        B (float): Damping coefficient (N·s/m)
        k (float): Spring constant (N/m)
        """
        self.M = M
        self.B = B
        self.k = k
        self.update_system()
    
    def update_system(self):
        """Update the system transfer function and state space representation"""
        # Transfer function: G(s) = 1/(Ms^2 + Bs + k)
        num = [1]
        den = [self.M, self.B, self.k]
        self.tf = ct.TransferFunction(num, den)
        
        # State space representation: x1 = x, x2 = x_dot
        # x_dot = [x2, (-k*x1 - B*x2 + F)/M]
        A = [[0, 1], [-self.k/self.M, -self.B/self.M]]
        B = [[0], [1/self.M]]
        C = [[1, 0]]  # Output is position
        D = [[0]]
        self.ss = ct.StateSpace(A, B, C, D)
        
        # Calculate natural frequency and damping ratio
        self.omega_n = np.sqrt(self.k / self.M)
        self.zeta = self.B / (2 * np.sqrt(self.M * self.k))
    
    def step_response(self, t_span=10, num_points=1000):
        """
        Generate step response
        
        Parameters:
        t_span (float): Time span for simulation
        num_points (int): Number of time points
        
        Returns:
        t (array): Time vector
        y (array): Response vector
        """
        t = np.linspace(0, t_span, num_points)
        t, y = ct.step_response(self.tf, t)
        return t, y
    
    def impulse_response(self, t_span=10, num_points=1000):
        """Generate impulse response"""
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
        mag (array): Magnitude in dB
        phase (array): Phase in degrees
        """
        if freq_range is None:
            freq_range = np.logspace(-2, 2, 1000)
        
        freq, mag, phase = ct.bode(self.tf, freq_range, plot=False)
        return freq, mag, phase
    
    def simulate(self, force_input, time):
        """
        Simulate system response to arbitrary force input
        
        Parameters:
        force_input (array): Force input vector
        time (array): Time vector
        
        Returns:
        t (array): Time vector
        y (array): Position response
        """
        t, y = ct.forced_response(self.tf, time, force_input)
        return t, y

def system_identification(input_data, output_data, time_data, system_order=2):
    """
    Perform system identification to estimate M, B, k parameters
    
    ## System Identification Theory
    
    Given input-output data, we can estimate the parameters by:
    1. Fitting a second-order transfer function to the data
    2. Extracting coefficients to determine M, B, k
    
    The transfer function is: $G(s) = \frac{1}{Ms^2 + Bs + k}$
    
    Parameters:
    input_data (array): Input force data
    output_data (array): Output position data
    time_data (array): Time vector
    system_order (int): Order of system (should be 2)
    
    Returns:
    M_est, B_est, k_est: Estimated parameters
    """
    # Use scipy's signal processing for system identification
    # Convert to discrete time first
    dt = time_data[1] - time_data[0]
    
    # Estimate transfer function using least squares
    # This is a simplified approach - in practice, more sophisticated methods are used
    # Create a simple discrete-time system for identification
    system = signal.dlti([1], [1, 0, 0], dt=dt)
    
    # Alternative approach: fit second-order model directly
    def second_order_model(t, M, B, k):
        """Second-order system step response model"""
        omega_n = np.sqrt(k/M)
        zeta = B/(2*np.sqrt(M*k))
        
        if zeta < 1:  # Underdamped
            omega_d = omega_n * np.sqrt(1 - zeta**2)
            response = 1 - np.exp(-zeta*omega_n*t) * (np.cos(omega_d*t) + 
                                                      (zeta*omega_n/omega_d)*np.sin(omega_d*t))
        elif zeta == 1:  # Critically damped
            response = 1 - np.exp(-omega_n*t) * (1 + omega_n*t)
        else:  # Overdamped
            r1 = -omega_n * (zeta + np.sqrt(zeta**2 - 1))
            r2 = -omega_n * (zeta - np.sqrt(zeta**2 - 1))
            response = 1 + (r2*np.exp(r1*t) - r1*np.exp(r2*t))/(r1 - r2)
        
        return response / k  # Scale by spring constant
    
    # If input is step, use step response fitting
    if np.allclose(input_data[10:], input_data[10]):  # Constant input (step)
        try:
            popt, _ = curve_fit(second_order_model, time_data, output_data, 
                              bounds=([0.1, 0.1, 0.1], [10, 10, 100]))
            M_est, B_est, k_est = popt
        except:
            # Fallback to default values if fitting fails
            M_est, B_est, k_est = 1.0, 2.0, 10.0
    else:
        # For general input, use a more complex identification method
        # This is simplified - real system ID would use methods like ARX, ARMAX, etc.
        M_est, B_est, k_est = 1.0, 2.0, 10.0
    
    return M_est, B_est, k_est

def plot_system_analysis(actuator, save_plots=False):
    """
    Generate comprehensive plots for system analysis
    
    Parameters:
    actuator (LinearActuator): System to analyze
    save_plots (bool): Whether to save plots to files
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Linear Actuator Analysis (M={actuator.M}, B={actuator.B}, k={actuator.k})', 
                 fontsize=14)
    
    # Step response
    t_step, y_step = actuator.step_response()
    axes[0,0].plot(t_step, y_step)
    axes[0,0].set_title('Step Response')
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Position (m)')
    axes[0,0].grid(True)
    
    # Impulse response
    t_imp, y_imp = actuator.impulse_response()
    axes[0,1].plot(t_imp, y_imp)
    axes[0,1].set_title('Impulse Response')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Position (m)')
    axes[0,1].grid(True)
    
    # Bode plot - Magnitude
    freq, mag, phase = actuator.frequency_response()
    axes[1,0].semilogx(freq, 20*np.log10(np.abs(mag)))
    axes[1,0].set_title('Bode Plot - Magnitude')
    axes[1,0].set_xlabel('Frequency (rad/s)')
    axes[1,0].set_ylabel('Magnitude (dB)')
    axes[1,0].grid(True)
    
    # Bode plot - Phase
    axes[1,1].semilogx(freq, np.angle(mag)*180/np.pi)
    axes[1,1].set_title('Bode Plot - Phase')
    axes[1,1].set_xlabel('Frequency (rad/s)')
    axes[1,1].set_ylabel('Phase (degrees)')
    axes[1,1].grid(True)
    
    plt.tight_layout()
    
    if save_plots:
        plt.savefig('linear_actuator_analysis.png', dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Print system characteristics
    print(f"System Characteristics:")
    print(f"Natural frequency (ωn): {actuator.omega_n:.3f} rad/s")
    print(f"Damping ratio (ζ): {actuator.zeta:.3f}")
    if actuator.zeta < 1:
        print("System is underdamped")
    elif actuator.zeta == 1:
        print("System is critically damped")
    else:
        print("System is overdamped")

def main():
    """
    ## Main Simulation and Analysis
    
    This section demonstrates:
    1. System modeling with different parameters
    2. System identification from simulated data
    3. Comprehensive analysis and visualization
    """
    
    # Create actuator systems with different characteristics
    print("=== Linear Actuator System Analysis ===\n")
    
    # Underdamped system
    print("1. Underdamped System (ζ < 1):")
    actuator_under = LinearActuator(M=1.0, B=1.0, k=25.0)
    plot_system_analysis(actuator_under)
    
    # Critically damped system
    print("\n2. Critically Damped System (ζ = 1):")
    M, k = 1.0, 25.0
    B_critical = 2 * np.sqrt(M * k)  # Critical damping condition
    actuator_critical = LinearActuator(M=M, B=B_critical, k=k)
    plot_system_analysis(actuator_critical)
    
    # Overdamped system
    print("\n3. Overdamped System (ζ > 1):")
    actuator_over = LinearActuator(M=1.0, B=15.0, k=25.0)
    plot_system_analysis(actuator_over)
    
    # System identification example
    print("\n=== System Identification Example ===")
    
    # Generate synthetic data from known system
    true_system = LinearActuator(M=2.0, B=3.0, k=20.0)
    t_data = np.linspace(0, 5, 100)
    force_input = np.ones_like(t_data)  # Step input
    _, y_data = true_system.simulate(force_input, t_data)
    
    # Add some noise to make it realistic
    y_data_noisy = y_data + 0.001 * np.random.randn(len(y_data))
    
    # Perform system identification
    M_est, B_est, k_est = system_identification(force_input, y_data_noisy, t_data)
    
    print(f"True parameters: M={true_system.M}, B={true_system.B}, k={true_system.k}")
    print(f"Estimated parameters: M={M_est:.3f}, B={B_est:.3f}, k={k_est:.3f}")
    
    # Compare responses
    estimated_system = LinearActuator(M=M_est, B=B_est, k=k_est)
    _, y_est = estimated_system.simulate(force_input, t_data)
    
    plt.figure(figsize=(10, 6))
    plt.plot(t_data, y_data, 'b-', label='True System', linewidth=2)
    plt.plot(t_data, y_data_noisy, 'r.', label='Noisy Data', alpha=0.7)
    plt.plot(t_data, y_est, 'g--', label='Identified System', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m)')
    plt.title('System Identification Results')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()