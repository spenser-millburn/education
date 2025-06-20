"""
Multi-Axis Motion Controller for SIMPL Automation System
Integrates PID control, trajectory generation, feed-forward, and safety monitoring
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time

from servo_motor import ServoMotor, create_x_axis_motor, create_y_axis_motor, create_z_axis_motor
from pid_controller import PIDController, create_position_controller, create_velocity_controller
from trajectory_generator import MultiAxisTrajectory, create_warehouse_constraints
from safety_monitor import SystemSafetyManager, create_warehouse_safety_limits


class ControllerState(Enum):
    """Motion controller operating states"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    HOMING = "homing"
    MOVING = "moving"
    HOLDING = "holding"
    FAULT = "fault"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class AxisState:
    """Complete state information for a single axis"""
    # Position and motion
    position: float = 0.0           # Current position (rad or m)
    velocity: float = 0.0           # Current velocity (rad/s or m/s)
    acceleration: float = 0.0       # Current acceleration (rad/s² or m/s²)
    
    # Control signals
    setpoint: float = 0.0           # Position setpoint
    velocity_setpoint: float = 0.0  # Velocity setpoint
    control_output: float = 0.0     # Controller output
    feedforward: float = 0.0        # Feed-forward contribution
    
    # Motor state
    motor_current: float = 0.0      # Motor current (A)
    motor_voltage: float = 0.0      # Applied voltage (V)
    motor_temperature: float = 25.0 # Motor temperature (°C)
    
    # Status
    enabled: bool = False           # Axis enabled
    homed: bool = False            # Axis has been homed
    in_position: bool = False      # Within position tolerance
    moving: bool = False           # Currently executing motion
    

class MotionController:
    """
    Multi-axis motion controller for SIMPL warehouse automation system.
    
    Integrates:
    - Multi-axis trajectory generation
    - PID position control with feed-forward
    - Safety monitoring and fault detection
    - Real-time control loop at 100Hz
    """
    
    def __init__(self, axis_names: List[str] = None):
        if axis_names is None:
            axis_names = ['X', 'Y', 'Z']
        
        self.axis_names = axis_names
        self.dt = 0.01  # 100Hz control loop
        
        # Initialize system components
        self._initialize_motors()
        self._initialize_controllers()
        self._initialize_trajectory_generator()
        self._initialize_safety_system()
        
        # System state
        self.controller_state = ControllerState.DISABLED
        self.axis_states: Dict[str, AxisState] = {axis: AxisState() for axis in axis_names}
        
        # Control performance tracking
        self.cycle_time = 0.0
        self.max_cycle_time = 0.0
        self.control_loop_overruns = 0
        
        # Motion tolerances
        self.position_tolerance = 0.001  # Position tolerance for "in position"
        self.velocity_tolerance = 0.01   # Velocity tolerance for "at rest"
        
        # Feed-forward parameters
        self.gravity_compensation = {'Y': 0.5}  # Gravity torque for Y-axis
        self.friction_compensation = {'X': 0.05, 'Y': 0.08, 'Z': 0.04}
        
    def _initialize_motors(self) -> None:
        """Initialize servo motor models for each axis"""
        self.motors: Dict[str, ServoMotor] = {}
        
        motor_factories = {
            'X': create_x_axis_motor,
            'Y': create_y_axis_motor,
            'Z': create_z_axis_motor
        }
        
        for axis in self.axis_names:
            if axis in motor_factories:
                self.motors[axis] = motor_factories[axis]()
            else:
                # Default motor for unknown axes
                self.motors[axis] = create_x_axis_motor()
                self.motors[axis].axis_name = axis
    
    def _initialize_controllers(self) -> None:
        """Initialize PID controllers for each axis"""
        self.position_controllers: Dict[str, PIDController] = {}
        
        for axis in self.axis_names:
            # Create position controller with appropriate tuning
            aggressive = (axis == 'X')  # X-axis can be more aggressive
            self.position_controllers[axis] = create_position_controller(axis, aggressive)
    
    def _initialize_trajectory_generator(self) -> None:
        """Initialize multi-axis trajectory generator"""
        constraints = create_warehouse_constraints()
        self.trajectory = MultiAxisTrajectory(self.axis_names, constraints)
    
    def _initialize_safety_system(self) -> None:
        """Initialize safety monitoring system"""
        self.safety_manager = SystemSafetyManager(self.axis_names)
        
        # Add monitors for each axis
        safety_limits = create_warehouse_safety_limits()
        for axis in self.axis_names:
            if axis in safety_limits:
                self.safety_manager.add_axis_monitor(axis, safety_limits[axis])
        
        # Register emergency stop callback
        self.safety_manager.add_system_fault_callback(self._emergency_stop_callback)
    
    def _emergency_stop_callback(self, fault) -> None:
        """Callback for emergency stop events"""
        print(f"EMERGENCY STOP TRIGGERED: {fault.message}")
        self.controller_state = ControllerState.EMERGENCY_STOP
        
        # Stop all motion immediately
        self.trajectory.stop()
        
        # Disable all axes
        for axis in self.axis_names:
            self.axis_states[axis].enabled = False
    
    def enable_system(self) -> bool:
        """Enable the motion control system"""
        if self.controller_state == ControllerState.EMERGENCY_STOP:
            # Cannot enable during emergency stop
            return False
        
        # Reset all controllers
        for controller in self.position_controllers.values():
            controller.reset()
        
        # Enable all axes
        for axis in self.axis_names:
            self.axis_states[axis].enabled = True
        
        self.controller_state = ControllerState.ENABLED
        return True
    
    def disable_system(self) -> None:
        """Disable the motion control system"""
        # Stop any active motion
        self.trajectory.stop()
        
        # Disable all axes
        for axis in self.axis_names:
            self.axis_states[axis].enabled = False
        
        self.controller_state = ControllerState.DISABLED
    
    def emergency_stop(self, reason: str = "Manual emergency stop") -> None:
        """Trigger emergency stop"""
        self.safety_manager.system_emergency_stop(reason)
    
    def reset_emergency_stop(self) -> bool:
        """Reset emergency stop if conditions are safe"""
        if self.safety_manager.reset_system_emergency_stop():
            self.controller_state = ControllerState.DISABLED
            return True
        return False
    
    def start_coordinated_move(self, target_positions: Dict[str, float],
                             start_velocities: Optional[Dict[str, float]] = None,
                             end_velocities: Optional[Dict[str, float]] = None) -> bool:
        """
        Start coordinated multi-axis move to target positions.
        
        Args:
            target_positions: Target position for each axis
            start_velocities: Optional starting velocities (default: current velocity)
            end_velocities: Optional ending velocities (default: 0)
            
        Returns:
            True if move started successfully, False otherwise
        """
        if self.controller_state not in [ControllerState.ENABLED, ControllerState.HOLDING]:
            return False
        
        # Get current positions
        current_positions = {axis: state.position for axis, state in self.axis_states.items()}
        
        # Use current velocities if not specified
        if start_velocities is None:
            start_velocities = {axis: state.velocity for axis, state in self.axis_states.items()}
        
        # Generate coordinated trajectory
        self.trajectory.generate_coordinated_move(
            current_positions, target_positions, start_velocities, end_velocities
        )
        
        self.controller_state = ControllerState.MOVING
        
        # Update axis states
        for axis in self.axis_names:
            self.axis_states[axis].moving = True
            self.axis_states[axis].in_position = False
        
        return True
    
    def update(self, dt: Optional[float] = None) -> None:
        """
        Main control loop update - call at 100Hz
        
        Args:
            dt: Time step (uses default if None)
        """
        if dt is None:
            dt = self.dt
        
        start_time = time.time()
        
        # Skip control if in emergency stop or disabled
        if self.controller_state in [ControllerState.EMERGENCY_STOP, ControllerState.DISABLED]:
            return
        
        # Update trajectory generator
        if self.controller_state == ControllerState.MOVING:
            trajectory_setpoints = self.trajectory.update(dt)
            
            # Check if trajectory is complete
            if self.trajectory.is_complete():
                self.controller_state = ControllerState.HOLDING
                for axis in self.axis_names:
                    self.axis_states[axis].moving = False
        else:
            # Use current positions as setpoints when not moving
            trajectory_setpoints = {
                axis: (state.position, 0.0, 0.0) for axis, state in self.axis_states.items()
            }
        
        # Update each axis
        for axis in self.axis_names:
            self._update_axis(axis, trajectory_setpoints.get(axis, (0.0, 0.0, 0.0)), dt)
        
        # Update safety monitoring
        self._update_safety_monitoring()
        
        # Update performance metrics
        cycle_time = time.time() - start_time
        self.cycle_time = cycle_time
        self.max_cycle_time = max(self.max_cycle_time, cycle_time)
        
        if cycle_time > dt * 1.5:  # Control loop overrun
            self.control_loop_overruns += 1
    
    def _update_axis(self, axis: str, setpoints: Tuple[float, float, float], dt: float) -> None:
        """Update control for a single axis"""
        if axis not in self.axis_states or not self.axis_states[axis].enabled:
            return
        
        state = self.axis_states[axis]
        motor = self.motors[axis]
        controller = self.position_controllers[axis]
        
        # Extract setpoints
        position_setpoint, velocity_setpoint, acceleration_setpoint = setpoints
        
        # Update motor simulation
        motor.update(dt)
        
        # Get current motor state
        motor_position, motor_velocity, motor_current = motor.get_state()
        
        # Calculate feed-forward compensation
        feedforward = self._calculate_feedforward(axis, velocity_setpoint, acceleration_setpoint)
        
        # Update position controller
        controller.set_setpoint(position_setpoint)
        control_output = controller.update(motor_position, dt, feedforward)
        
        # Apply control output to motor
        motor.apply_voltage(control_output)
        
        # Update axis state
        state.position = motor_position
        state.velocity = motor_velocity
        state.acceleration = (motor_velocity - state.velocity) / dt  # Numerical differentiation
        state.setpoint = position_setpoint
        state.velocity_setpoint = velocity_setpoint
        state.control_output = control_output
        state.feedforward = feedforward
        state.motor_current = motor_current
        state.motor_voltage = control_output
        
        # Check if in position
        position_error = abs(position_setpoint - motor_position)
        velocity_magnitude = abs(motor_velocity)
        state.in_position = (position_error < self.position_tolerance and 
                           velocity_magnitude < self.velocity_tolerance)
    
    def _calculate_feedforward(self, axis: str, velocity_setpoint: float, 
                             acceleration_setpoint: float) -> float:
        """Calculate feed-forward compensation for an axis"""
        feedforward = 0.0
        
        # Gravity compensation (mainly for Y-axis)
        if axis in self.gravity_compensation:
            feedforward += self.gravity_compensation[axis]
        
        # Friction compensation
        if axis in self.friction_compensation and abs(velocity_setpoint) > 0.01:
            friction_torque = self.friction_compensation[axis] * np.sign(velocity_setpoint)
            feedforward += friction_torque
        
        # Acceleration feed-forward (simplified)
        if abs(acceleration_setpoint) > 0.01:
            # Use motor inertia for acceleration compensation
            motor = self.motors[axis]
            inertia_feedforward = motor.params.inertia * acceleration_setpoint
            feedforward += inertia_feedforward * 0.1  # Scale factor
        
        return feedforward
    
    def _update_safety_monitoring(self) -> None:
        """Update safety monitoring for all axes"""
        # Prepare state data for safety monitoring
        axis_states_for_safety = {}
        
        for axis, state in self.axis_states.items():
            axis_states_for_safety[axis] = {
                'position': state.position,
                'velocity': state.velocity,
                'acceleration': state.acceleration,
                'current': state.motor_current,
                'setpoint': state.setpoint,
                'control_output': state.control_output
            }
        
        # Update safety monitoring
        new_faults = self.safety_manager.update_all_axes(axis_states_for_safety)
        
        # Log any new faults
        for axis, faults in new_faults.items():
            for fault in faults:
                print(f"FAULT [{axis}]: {fault.fault_type.value} - {fault.message}")
    
    def home_axis(self, axis: str) -> bool:
        """Home a single axis (simplified implementation)"""
        if axis not in self.axis_states:
            return False
        
        # Simple homing: move to position 0
        self.start_coordinated_move({axis: 0.0})
        
        # Mark as homed when move completes
        # In real implementation, this would involve limit switches and encoders
        self.axis_states[axis].homed = True
        return True
    
    def home_all_axes(self) -> bool:
        """Home all axes sequentially"""
        if self.controller_state != ControllerState.ENABLED:
            return False
        
        self.controller_state = ControllerState.HOMING
        
        # Move all axes to home position
        home_positions = {axis: 0.0 for axis in self.axis_names}
        success = self.start_coordinated_move(home_positions)
        
        if success:
            for axis in self.axis_names:
                self.axis_states[axis].homed = True
        
        return success
    
    def is_motion_complete(self) -> bool:
        """Check if all axes have completed motion and are in position"""
        if self.controller_state != ControllerState.HOLDING:
            return False
        
        return all(state.in_position for state in self.axis_states.values())
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        # Get safety status
        safety_status = self.safety_manager.get_system_status()
        
        # Compile axis states
        axis_status = {}
        for axis, state in self.axis_states.items():
            axis_status[axis] = {
                'position': state.position,
                'velocity': state.velocity,
                'setpoint': state.setpoint,
                'enabled': state.enabled,
                'homed': state.homed,
                'in_position': state.in_position,
                'moving': state.moving,
                'control_output': state.control_output,
                'motor_current': state.motor_current
            }
        
        return {
            'controller_state': self.controller_state.value,
            'trajectory_active': self.trajectory.is_active,
            'trajectory_progress': self.trajectory.get_progress(),
            'cycle_time': self.cycle_time,
            'max_cycle_time': self.max_cycle_time,
            'control_overruns': self.control_loop_overruns,
            'axes': axis_status,
            'safety': safety_status
        }
    
    def set_axis_gains(self, axis: str, kp: float, ki: float, kd: float) -> bool:
        """Set PID gains for a specific axis"""
        if axis not in self.position_controllers:
            return False
        
        from pid_controller import PIDGains
        gains = PIDGains(kp=kp, ki=ki, kd=kd)
        self.position_controllers[axis].set_gains(gains)
        return True
    
    def get_axis_performance(self, axis: str) -> Optional[Dict[str, float]]:
        """Get performance metrics for a specific axis"""
        if axis not in self.position_controllers:
            return None
        
        return self.position_controllers[axis].get_performance_metrics()


if __name__ == "__main__":
    # Test motion controller
    print("Testing SIMPL Motion Controller")
    
    controller = MotionController(['X', 'Y', 'Z'])
    
    # Enable system
    if controller.enable_system():
        print("System enabled successfully")
    
    # Start a coordinated move
    target_positions = {'X': 1.0, 'Y': 0.5, 'Z': -0.3}
    if controller.start_coordinated_move(target_positions):
        print(f"Started move to: {target_positions}")
    
    # Simulate control loop
    dt = 0.01
    max_time = 5.0
    time_elapsed = 0.0
    
    print("\nSimulating motion...")
    while time_elapsed < max_time and not controller.is_motion_complete():
        controller.update(dt)
        time_elapsed += dt
        
        # Print status every 0.5 seconds
        if int(time_elapsed * 10) % 5 == 0:
            status = controller.get_system_status()
            print(f"t={time_elapsed:.1f}s: State={status['controller_state']}, "
                  f"Progress={status['trajectory_progress']:.1%}")
            
            # Print axis positions
            for axis, axis_status in status['axes'].items():
                print(f"  {axis}: pos={axis_status['position']:.3f}, "
                      f"in_pos={axis_status['in_position']}")
    
    # Final status
    final_status = controller.get_system_status()
    print(f"\nFinal Status:")
    print(f"Controller State: {final_status['controller_state']}")
    print(f"Motion Complete: {controller.is_motion_complete()}")
    print(f"Max Cycle Time: {final_status['max_cycle_time']:.4f}s")
    print(f"Control Overruns: {final_status['control_overruns']}")
    
    # Test emergency stop
    print("\nTesting emergency stop...")
    controller.emergency_stop("Test emergency stop")
    
    status = controller.get_system_status()
    print(f"After E-Stop: {status['controller_state']}")
    print(f"Safety Status: {status['safety']['system_emergency_stop']}")