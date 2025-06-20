"""
Servo Motor Model for SIMPL Automation System
Implements mathematical model of brushless servo motor with encoder feedback
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class MotorParameters:
    """Physical parameters for servo motor model"""
    # Motor constants
    motor_constant: float = 0.1      # Nm/A - Motor torque constant
    back_emf_constant: float = 0.1   # V⋅s/rad - Back EMF constant
    resistance: float = 2.0          # Ω - Motor resistance
    inductance: float = 0.01         # H - Motor inductance
    
    # Mechanical parameters
    inertia: float = 0.001           # kg⋅m² - Rotor + load inertia
    damping: float = 0.01            # N⋅m⋅s/rad - Viscous damping
    static_friction: float = 0.05    # N⋅m - Static friction torque
    coulomb_friction: float = 0.03   # N⋅m - Coulomb friction torque
    
    # Gearing
    gear_ratio: float = 10.0         # Output shaft revolutions per motor revolution
    gear_efficiency: float = 0.95    # Gear train efficiency


class ServoMotor:
    """
    Mathematical model of a servo motor for simulation and control design.
    
    Models electrical dynamics, mechanical dynamics, friction, and gearing.
    Provides position, velocity, and current feedback similar to real hardware.
    """
    
    def __init__(self, params: MotorParameters, axis_name: str = "Unknown"):
        self.params = params
        self.axis_name = axis_name
        
        # State variables [position, velocity, current]
        self.position = 0.0      # rad (motor shaft)
        self.velocity = 0.0      # rad/s (motor shaft)
        self.current = 0.0       # A
        
        # External disturbances
        self.external_torque = 0.0  # N⋅m
        self.gravity_torque = 0.0   # N⋅m (for vertical axes)
        
        # Internal states
        self._voltage_applied = 0.0
        self._dt = 0.001  # Default timestep
        
    def set_gravity_torque(self, torque: float) -> None:
        """Set constant gravity torque (for Y-axis)"""
        self.gravity_torque = torque
        
    def set_external_disturbance(self, torque: float) -> None:
        """Set external disturbance torque"""
        self.external_torque = torque
        
    def apply_voltage(self, voltage: float) -> None:
        """Apply voltage to motor terminals"""
        self._voltage_applied = voltage
        
    def update(self, dt: float) -> None:
        """
        Update motor state using numerical integration.
        
        Args:
            dt: Time step for integration (seconds)
        """
        self._dt = dt
        
        # Electrical dynamics: L*(di/dt) + R*i + Ke*ω = V
        back_emf = self.params.back_emf_constant * self.velocity
        current_derivative = (self._voltage_applied - self.params.resistance * self.current - back_emf) / self.params.inductance
        
        # Update current using Euler integration
        self.current += current_derivative * dt
        
        # Mechanical dynamics: J*(dω/dt) + B*ω = Tm - Tf - Text
        motor_torque = self.params.motor_constant * self.current
        
        # Friction model
        friction_torque = self._calculate_friction(self.velocity)
        
        # Total torque equation
        total_load_torque = (friction_torque + self.external_torque + self.gravity_torque) / self.params.gear_efficiency
        net_torque = motor_torque - self.params.damping * self.velocity - total_load_torque
        
        # Update velocity
        acceleration = net_torque / self.params.inertia
        self.velocity += acceleration * dt
        
        # Update position
        self.position += self.velocity * dt
        
    def _calculate_friction(self, velocity: float) -> float:
        """Calculate friction torque based on velocity"""
        if abs(velocity) < 1e-6:  # Near zero velocity
            # Static friction - opposes applied force up to static limit
            return 0.0  # Simplified - in reality depends on applied torque
        else:
            # Kinetic friction - opposes motion
            return self.params.coulomb_friction * np.sign(velocity)
    
    def get_output_position(self) -> float:
        """Get position at output shaft (after gearing)"""
        return self.position / self.params.gear_ratio
    
    def get_output_velocity(self) -> float:
        """Get velocity at output shaft (after gearing)"""
        return self.velocity / self.params.gear_ratio
    
    def get_encoder_reading(self, noise_std: float = 0.0) -> float:
        """Get encoder position reading with optional noise"""
        position = self.get_output_position()
        if noise_std > 0:
            position += np.random.normal(0, noise_std)
        return position
    
    def get_state(self) -> Tuple[float, float, float]:
        """Get current motor state [position, velocity, current]"""
        return (self.get_output_position(), self.get_output_velocity(), self.current)
    
    def reset(self) -> None:
        """Reset motor to initial state"""
        self.position = 0.0
        self.velocity = 0.0
        self.current = 0.0
        self.external_torque = 0.0
        self._voltage_applied = 0.0
    
    def get_transfer_function_params(self) -> dict:
        """
        Calculate transfer function parameters for control design.
        
        Returns:
            Dictionary with transfer function coefficients for G(s) = K/(s(Js+B))
        """
        # Motor transfer function from voltage to velocity
        Kt = self.params.motor_constant
        Ke = self.params.back_emf_constant
        R = self.params.resistance
        L = self.params.inductance
        J = self.params.inertia
        B = self.params.damping
        
        # Simplified first-order approximation (ignoring electrical dynamics)
        K = Kt / (R * B + Kt * Ke)  # DC gain
        tau = (R * J) / (R * B + Kt * Ke)  # Time constant
        
        return {
            'K': K,
            'tau': tau,
            'J_effective': J,
            'B_effective': B,
            'gear_ratio': self.params.gear_ratio
        }
    
    def __str__(self) -> str:
        """String representation of motor state"""
        pos_deg = np.degrees(self.get_output_position())
        vel_rpm = self.get_output_velocity() * 60 / (2 * np.pi)
        return (f"{self.axis_name} Motor - "
                f"Pos: {pos_deg:.2f}°, "
                f"Vel: {vel_rpm:.1f} RPM, "
                f"Current: {self.current:.2f} A")


# Factory functions for different SIMPL axes
def create_x_axis_motor() -> ServoMotor:
    """Create X-axis motor with typical horizontal axis parameters"""
    params = MotorParameters(
        motor_constant=0.15,
        inertia=0.002,      # Higher inertia due to horizontal load
        damping=0.015,
        gear_ratio=20.0,    # Higher gear ratio for precision
        static_friction=0.08,
        coulomb_friction=0.05
    )
    motor = ServoMotor(params, "X-Axis")
    return motor


def create_y_axis_motor() -> ServoMotor:
    """Create Y-axis motor with gravity compensation considerations"""
    params = MotorParameters(
        motor_constant=0.2,     # Higher torque for lifting
        inertia=0.003,          # Higher inertia due to vertical load
        damping=0.02,
        gear_ratio=50.0,        # High gear ratio for holding against gravity
        static_friction=0.1,
        coulomb_friction=0.07
    )
    motor = ServoMotor(params, "Y-Axis")
    # Set gravity torque (example: 0.5 Nm to lift typical warehouse payload)
    motor.set_gravity_torque(0.5)
    return motor


def create_z_axis_motor() -> ServoMotor:
    """Create Z-axis motor with moderate parameters"""
    params = MotorParameters(
        motor_constant=0.12,
        inertia=0.0015,
        damping=0.012,
        gear_ratio=15.0,
        static_friction=0.06,
        coulomb_friction=0.04
    )
    motor = ServoMotor(params, "Z-Axis")
    return motor


if __name__ == "__main__":
    # Simple test
    motor = create_x_axis_motor()
    print("X-Axis Motor Created")
    print(f"Transfer Function Parameters: {motor.get_transfer_function_params()}")
    
    # Simulate step input
    motor.apply_voltage(5.0)
    for i in range(100):
        motor.update(0.001)
        if i % 20 == 0:
            print(f"t={i*0.001:.3f}s: {motor}")