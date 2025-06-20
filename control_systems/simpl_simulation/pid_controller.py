"""
PID Controller Implementation for SIMPL Automation System
Includes anti-windup, derivative filtering, and gain scheduling capabilities
"""

import numpy as np
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ControllerMode(Enum):
    """Controller operating modes"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    DISABLED = "disabled"


@dataclass
class PIDGains:
    """PID controller gain parameters"""
    kp: float = 1.0      # Proportional gain
    ki: float = 0.0      # Integral gain
    kd: float = 0.0      # Derivative gain
    
    def __post_init__(self):
        """Validate gains are non-negative"""
        if self.kp < 0 or self.ki < 0 or self.kd < 0:
            raise ValueError("PID gains must be non-negative")


@dataclass
class PIDLimits:
    """PID controller limits and constraints"""
    output_min: float = -10.0        # Minimum controller output
    output_max: float = 10.0         # Maximum controller output
    integral_min: float = -5.0       # Integral windup limit (lower)
    integral_max: float = 5.0        # Integral windup limit (upper)
    derivative_filter_time: float = 0.1  # Derivative filter time constant (seconds)


class PIDController:
    """
    Advanced PID controller with anti-windup, derivative filtering, and gain scheduling.
    
    Features:
    - Proportional, Integral, and Derivative control actions
    - Anti-windup protection for integral term
    - Derivative filtering to reduce noise sensitivity
    - Bumpless transfer when changing setpoints or gains
    - Gain scheduling based on operating conditions
    - Manual/automatic mode switching
    """
    
    def __init__(self, gains: PIDGains, limits: PIDLimits, name: str = "PID"):
        self.gains = gains
        self.limits = limits
        self.name = name
        
        # Controller state
        self.mode = ControllerMode.AUTOMATIC
        self.setpoint = 0.0
        self.output = 0.0
        self.manual_output = 0.0
        
        # Internal state variables
        self._integral_sum = 0.0
        self._previous_error = 0.0
        self._previous_measurement = 0.0
        self._filtered_derivative = 0.0
        self._dt = 0.001
        
        # Performance tracking
        self._error_history = []
        self._output_history = []
        self._max_history_length = 1000
        
        # Gain scheduling
        self._gain_schedule = {}
        self._current_schedule_key = "default"
        
    def set_gains(self, gains: PIDGains) -> None:
        """Update PID gains with bumpless transfer"""
        self.gains = gains
        
    def set_setpoint(self, setpoint: float) -> None:
        """Set the desired setpoint"""
        self.setpoint = setpoint
        
    def set_mode(self, mode: ControllerMode) -> None:
        """Change controller mode"""
        if mode == ControllerMode.MANUAL and self.mode == ControllerMode.AUTOMATIC:
            # Switch to manual - preserve current output
            self.manual_output = self.output
        elif mode == ControllerMode.AUTOMATIC and self.mode == ControllerMode.MANUAL:
            # Switch to automatic - initialize for bumpless transfer
            self._initialize_for_bumpless_transfer()
            
        self.mode = mode
        
    def _initialize_for_bumpless_transfer(self) -> None:
        """Initialize controller state for smooth transition to automatic mode"""
        # Set integral sum to produce current manual output
        if self.gains.ki > 0:
            error = self.setpoint - self._previous_measurement
            proportional = self.gains.kp * error
            derivative = self.gains.kd * self._filtered_derivative
            self._integral_sum = (self.manual_output - proportional - derivative) / self.gains.ki
            
            # Clamp integral within limits
            self._integral_sum = np.clip(self._integral_sum, 
                                       self.limits.integral_min, 
                                       self.limits.integral_max)
    
    def update(self, measurement: float, dt: float, feedforward: float = 0.0) -> float:
        """
        Update PID controller and return control output.
        
        Args:
            measurement: Current process variable measurement
            dt: Time step since last update
            feedforward: Optional feedforward term
            
        Returns:
            Controller output (control signal)
        """
        self._dt = dt
        
        if self.mode == ControllerMode.DISABLED:
            self.output = 0.0
            return self.output
        elif self.mode == ControllerMode.MANUAL:
            self.output = self.manual_output
            return self.output
        
        # Calculate error
        error = self.setpoint - measurement
        
        # Proportional term
        proportional = self.gains.kp * error
        
        # Integral term with anti-windup
        self._integral_sum += error * dt
        
        # Anti-windup: clamp integral sum
        self._integral_sum = np.clip(self._integral_sum,
                                   self.limits.integral_min,
                                   self.limits.integral_max)
        
        integral = self.gains.ki * self._integral_sum
        
        # Derivative term with filtering (derivative on measurement to avoid setpoint kicks)
        measurement_derivative = (measurement - self._previous_measurement) / dt
        
        # Apply first-order filter to derivative
        alpha = dt / (self.limits.derivative_filter_time + dt)
        self._filtered_derivative = (1 - alpha) * self._filtered_derivative + alpha * measurement_derivative
        
        derivative = -self.gains.kd * self._filtered_derivative  # Negative because we use derivative of measurement
        
        # Calculate total output
        self.output = proportional + integral + derivative + feedforward
        
        # Output limiting
        self.output = np.clip(self.output, self.limits.output_min, self.limits.output_max)
        
        # Additional anti-windup: prevent integral buildup when output is saturated
        if self.output >= self.limits.output_max or self.output <= self.limits.output_min:
            if np.sign(error) == np.sign(self._integral_sum):
                # Don't let integral grow further in the direction of saturation
                self._integral_sum -= error * dt
        
        # Store history for analysis
        self._update_history(error)
        
        # Update previous values
        self._previous_error = error
        self._previous_measurement = measurement
        
        return self.output
    
    def _update_history(self, error: float) -> None:
        """Update performance history"""
        self._error_history.append(error)
        self._output_history.append(self.output)
        
        # Limit history length
        if len(self._error_history) > self._max_history_length:
            self._error_history.pop(0)
            self._output_history.pop(0)
    
    def reset(self) -> None:
        """Reset controller to initial state"""
        self._integral_sum = 0.0
        self._previous_error = 0.0
        self._previous_measurement = 0.0
        self._filtered_derivative = 0.0
        self.output = 0.0
        self._error_history.clear()
        self._output_history.clear()
    
    def set_manual_output(self, output: float) -> None:
        """Set manual output value (when in manual mode)"""
        self.manual_output = np.clip(output, self.limits.output_min, self.limits.output_max)
    
    def add_gain_schedule(self, key: str, gains: PIDGains) -> None:
        """Add a gain schedule for different operating conditions"""
        self._gain_schedule[key] = gains
    
    def select_gain_schedule(self, key: str) -> None:
        """Select active gain schedule"""
        if key in self._gain_schedule:
            self.gains = self._gain_schedule[key]
            self._current_schedule_key = key
        else:
            raise ValueError(f"Gain schedule '{key}' not found")
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics from recent history"""
        if len(self._error_history) < 10:
            return {"error_rms": 0.0, "error_mean": 0.0, "output_std": 0.0}
        
        errors = np.array(self._error_history[-100:])  # Last 100 samples
        outputs = np.array(self._output_history[-100:])
        
        return {
            "error_rms": np.sqrt(np.mean(errors**2)),
            "error_mean": np.mean(errors),
            "error_std": np.std(errors),
            "output_mean": np.mean(outputs),
            "output_std": np.std(outputs),
            "output_saturation_percent": np.sum(np.abs(outputs) >= 0.95 * self.limits.output_max) / len(outputs) * 100
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get complete controller state for monitoring/debugging"""
        return {
            "mode": self.mode.value,
            "setpoint": self.setpoint,
            "output": self.output,
            "gains": {"kp": self.gains.kp, "ki": self.gains.ki, "kd": self.gains.kd},
            "integral_sum": self._integral_sum,
            "filtered_derivative": self._filtered_derivative,
            "gain_schedule": self._current_schedule_key,
            "performance": self.get_performance_metrics()
        }
    
    def __str__(self) -> str:
        """String representation of controller state"""
        return (f"{self.name} PID - Mode: {self.mode.value}, "
                f"SP: {self.setpoint:.3f}, "
                f"Output: {self.output:.3f}, "
                f"Gains: P={self.gains.kp:.2f}, I={self.gains.ki:.2f}, D={self.gains.kd:.2f}")


def create_position_controller(axis_name: str, aggressive: bool = False) -> PIDController:
    """
    Factory function to create position controller with typical gains.
    
    Args:
        axis_name: Name of the axis (for identification)
        aggressive: If True, use more aggressive tuning
        
    Returns:
        Configured PID controller
    """
    if aggressive:
        gains = PIDGains(kp=50.0, ki=10.0, kd=2.0)
    else:
        gains = PIDGains(kp=20.0, ki=5.0, kd=1.0)
    
    limits = PIDLimits(
        output_min=-10.0,
        output_max=10.0,
        integral_min=-2.0,
        integral_max=2.0,
        derivative_filter_time=0.05
    )
    
    controller = PIDController(gains, limits, f"{axis_name}_Position")
    
    # Add gain schedules for different payloads
    light_gains = PIDGains(kp=gains.kp * 0.8, ki=gains.ki * 0.6, kd=gains.kd * 1.2)
    heavy_gains = PIDGains(kp=gains.kp * 1.2, ki=gains.ki * 1.4, kd=gains.kd * 0.8)
    
    controller.add_gain_schedule("light_payload", light_gains)
    controller.add_gain_schedule("heavy_payload", heavy_gains)
    controller.add_gain_schedule("default", gains)
    
    return controller


def create_velocity_controller(axis_name: str) -> PIDController:
    """Factory function to create velocity controller (inner loop)"""
    gains = PIDGains(kp=2.0, ki=10.0, kd=0.1)
    
    limits = PIDLimits(
        output_min=-10.0,
        output_max=10.0,
        integral_min=-1.0,
        integral_max=1.0,
        derivative_filter_time=0.01
    )
    
    return PIDController(gains, limits, f"{axis_name}_Velocity")


if __name__ == "__main__":
    # Test PID controller
    controller = create_position_controller("Test", aggressive=False)
    controller.set_setpoint(1.0)
    
    print(f"Created controller: {controller}")
    
    # Simulate step response
    measurement = 0.0
    dt = 0.001
    
    for i in range(50):
        output = controller.update(measurement, dt)
        # Simple integrator plant
        measurement += output * dt * 0.1
        
        if i % 10 == 0:
            print(f"t={i*dt:.3f}: measurement={measurement:.3f}, output={output:.3f}")
    
    print(f"Final performance: {controller.get_performance_metrics()}")