"""
Safety Monitoring System for SIMPL Automation
Implements fault detection, safety limits, and emergency response
"""

import numpy as np
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import time
from collections import deque


class SafetyLevel(Enum):
    """Safety severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class FaultType(Enum):
    """Types of faults that can be detected"""
    POSITION_LIMIT = "position_limit"
    VELOCITY_LIMIT = "velocity_limit"
    ACCELERATION_LIMIT = "acceleration_limit"
    CURRENT_LIMIT = "current_limit"
    POSITION_ERROR = "position_error"
    CONTROL_SATURATION = "control_saturation"
    SENSOR_FAULT = "sensor_fault"
    COMMUNICATION_FAULT = "communication_fault"
    MECHANICAL_BINDING = "mechanical_binding"
    TEMPERATURE_FAULT = "temperature_fault"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class SafetyLimits:
    """Safety limits for a single axis"""
    position_min: float = -10.0      # Minimum position limit
    position_max: float = 10.0       # Maximum position limit
    velocity_max: float = 5.0        # Maximum velocity magnitude
    acceleration_max: float = 20.0   # Maximum acceleration magnitude
    current_max: float = 10.0        # Maximum current magnitude
    position_error_max: float = 0.1  # Maximum allowable position error
    control_saturation_time: float = 1.0  # Max time for control saturation
    
    
@dataclass
class FaultEvent:
    """Record of a fault event"""
    timestamp: float
    fault_type: FaultType
    safety_level: SafetyLevel
    axis: str
    value: float
    limit: float
    message: str
    id: int = field(default_factory=lambda: int(time.time() * 1000000))


class SafetyMonitor:
    """
    Safety monitoring system for individual axis.
    Monitors limits, detects faults, and triggers appropriate responses.
    """
    
    def __init__(self, axis_name: str, limits: SafetyLimits):
        self.axis_name = axis_name
        self.limits = limits
        
        # Fault detection state
        self.active_faults: Dict[FaultType, FaultEvent] = {}
        self.fault_history: List[FaultEvent] = []
        self.max_history_length = 1000
        
        # Monitoring state
        self.last_position = 0.0
        self.last_velocity = 0.0
        self.last_update_time = time.time()
        
        # Control saturation monitoring
        self.control_saturation_start_time = None
        self.control_saturation_duration = 0.0
        
        # Sensor validation
        self.sensor_readings = deque(maxlen=10)
        self.sensor_noise_threshold = 0.01
        
        # Emergency stop state
        self.emergency_stop_active = False
        self.emergency_stop_callback: Optional[Callable] = None
        
        # Performance tracking
        self.position_error_history = deque(maxlen=100)
        self.velocity_history = deque(maxlen=100)
        
    def set_emergency_stop_callback(self, callback: Callable) -> None:
        """Set callback function to be called on emergency stop"""
        self.emergency_stop_callback = callback
        
    def update(self, position: float, velocity: float, acceleration: float,
               current: float, setpoint: float, control_output: float,
               control_output_limits: tuple = (-10.0, 10.0)) -> List[FaultEvent]:
        """
        Update safety monitor with current system state.
        
        Args:
            position: Current position
            velocity: Current velocity  
            acceleration: Current acceleration
            current: Motor current
            setpoint: Position setpoint
            control_output: Controller output
            control_output_limits: Controller output limits (min, max)
            
        Returns:
            List of new fault events detected this update
        """
        current_time = time.time()
        new_faults = []
        
        # Calculate position error
        position_error = abs(setpoint - position)
        
        # Store for trend analysis
        self.position_error_history.append(position_error)
        self.velocity_history.append(velocity)
        self.sensor_readings.append(position)
        
        # Check position limits
        if position < self.limits.position_min:
            fault = self._create_fault(FaultType.POSITION_LIMIT, SafetyLevel.CRITICAL,
                                     position, self.limits.position_min,
                                     f"Position {position:.3f} below minimum limit {self.limits.position_min}")
            new_faults.append(fault)
            
        elif position > self.limits.position_max:
            fault = self._create_fault(FaultType.POSITION_LIMIT, SafetyLevel.CRITICAL,
                                     position, self.limits.position_max,
                                     f"Position {position:.3f} above maximum limit {self.limits.position_max}")
            new_faults.append(fault)
        else:
            self._clear_fault(FaultType.POSITION_LIMIT)
        
        # Check velocity limits
        if abs(velocity) > self.limits.velocity_max:
            fault = self._create_fault(FaultType.VELOCITY_LIMIT, SafetyLevel.CRITICAL,
                                     abs(velocity), self.limits.velocity_max,
                                     f"Velocity {velocity:.3f} exceeds limit {self.limits.velocity_max}")
            new_faults.append(fault)
        else:
            self._clear_fault(FaultType.VELOCITY_LIMIT)
        
        # Check acceleration limits
        if abs(acceleration) > self.limits.acceleration_max:
            fault = self._create_fault(FaultType.ACCELERATION_LIMIT, SafetyLevel.WARNING,
                                     abs(acceleration), self.limits.acceleration_max,
                                     f"Acceleration {acceleration:.3f} exceeds limit {self.limits.acceleration_max}")
            new_faults.append(fault)
        else:
            self._clear_fault(FaultType.ACCELERATION_LIMIT)
        
        # Check current limits
        if abs(current) > self.limits.current_max:
            fault = self._create_fault(FaultType.CURRENT_LIMIT, SafetyLevel.WARNING,
                                     abs(current), self.limits.current_max,
                                     f"Current {current:.3f} exceeds limit {self.limits.current_max}")
            new_faults.append(fault)
        else:
            self._clear_fault(FaultType.CURRENT_LIMIT)
        
        # Check position error
        if position_error > self.limits.position_error_max:
            fault = self._create_fault(FaultType.POSITION_ERROR, SafetyLevel.WARNING,
                                     position_error, self.limits.position_error_max,
                                     f"Position error {position_error:.4f} exceeds limit {self.limits.position_error_max}")
            new_faults.append(fault)
        else:
            self._clear_fault(FaultType.POSITION_ERROR)
        
        # Check control saturation
        control_min, control_max = control_output_limits
        is_saturated = (control_output <= control_min + 0.01) or (control_output >= control_max - 0.01)
        
        if is_saturated:
            if self.control_saturation_start_time is None:
                self.control_saturation_start_time = current_time
            
            self.control_saturation_duration = current_time - self.control_saturation_start_time
            
            if self.control_saturation_duration > self.limits.control_saturation_time:
                fault = self._create_fault(FaultType.CONTROL_SATURATION, SafetyLevel.WARNING,
                                         self.control_saturation_duration, self.limits.control_saturation_time,
                                         f"Control saturated for {self.control_saturation_duration:.2f}s")
                new_faults.append(fault)
        else:
            self.control_saturation_start_time = None
            self.control_saturation_duration = 0.0
            self._clear_fault(FaultType.CONTROL_SATURATION)
        
        # Check for sensor faults (excessive noise or stuck readings)
        if len(self.sensor_readings) >= 5:
            sensor_noise = np.std(list(self.sensor_readings)[-5:])
            if sensor_noise > self.sensor_noise_threshold:
                fault = self._create_fault(FaultType.SENSOR_FAULT, SafetyLevel.WARNING,
                                         sensor_noise, self.sensor_noise_threshold,
                                         f"Excessive sensor noise: {sensor_noise:.4f}")
                new_faults.append(fault)
            else:
                self._clear_fault(FaultType.SENSOR_FAULT)
        
        # Check for mechanical binding (high current with low velocity)
        if abs(current) > 0.7 * self.limits.current_max and abs(velocity) < 0.1:
            fault = self._create_fault(FaultType.MECHANICAL_BINDING, SafetyLevel.CRITICAL,
                                     abs(current), 0.7 * self.limits.current_max,
                                     f"Possible mechanical binding: high current {current:.2f}A, low velocity {velocity:.3f}")
            new_faults.append(fault)
        else:
            self._clear_fault(FaultType.MECHANICAL_BINDING)
        
        # Update state for next iteration
        self.last_position = position
        self.last_velocity = velocity
        self.last_update_time = current_time
        
        return new_faults
    
    def _create_fault(self, fault_type: FaultType, level: SafetyLevel,
                     value: float, limit: float, message: str) -> FaultEvent:
        """Create and register a new fault event"""
        fault = FaultEvent(
            timestamp=time.time(),
            fault_type=fault_type,
            safety_level=level,
            axis=self.axis_name,
            value=value,
            limit=limit,
            message=message
        )
        
        # Add to active faults and history
        self.active_faults[fault_type] = fault
        self.fault_history.append(fault)
        
        # Limit history length
        if len(self.fault_history) > self.max_history_length:
            self.fault_history.pop(0)
        
        # Trigger emergency stop for critical/emergency faults
        if level in [SafetyLevel.CRITICAL, SafetyLevel.EMERGENCY]:
            self._trigger_emergency_action(fault)
        
        return fault
    
    def _clear_fault(self, fault_type: FaultType) -> None:
        """Clear an active fault"""
        if fault_type in self.active_faults:
            del self.active_faults[fault_type]
    
    def _trigger_emergency_action(self, fault: FaultEvent) -> None:
        """Trigger emergency response for critical faults"""
        self.emergency_stop_active = True
        
        if self.emergency_stop_callback:
            self.emergency_stop_callback(fault)
    
    def emergency_stop(self, reason: str = "Manual emergency stop") -> None:
        """Manually trigger emergency stop"""
        fault = FaultEvent(
            timestamp=time.time(),
            fault_type=FaultType.EMERGENCY_STOP,
            safety_level=SafetyLevel.EMERGENCY,
            axis=self.axis_name,
            value=0.0,
            limit=0.0,
            message=reason
        )
        
        self.emergency_stop_active = True
        self.active_faults[FaultType.EMERGENCY_STOP] = fault
        self.fault_history.append(fault)
        
        if self.emergency_stop_callback:
            self.emergency_stop_callback(fault)
    
    def reset_emergency_stop(self) -> bool:
        """Reset emergency stop if conditions are safe"""
        # Check if any critical faults are still active
        critical_faults = [f for f in self.active_faults.values() 
                          if f.safety_level in [SafetyLevel.CRITICAL, SafetyLevel.EMERGENCY]]
        
        if not critical_faults:
            self.emergency_stop_active = False
            self._clear_fault(FaultType.EMERGENCY_STOP)
            return True
        
        return False
    
    def get_active_faults(self) -> List[FaultEvent]:
        """Get list of currently active faults"""
        return list(self.active_faults.values())
    
    def get_fault_summary(self) -> Dict[str, Any]:
        """Get summary of fault status"""
        active_by_level = {}
        for level in SafetyLevel:
            active_by_level[level.value] = [
                f for f in self.active_faults.values() if f.safety_level == level
            ]
        
        return {
            "axis": self.axis_name,
            "emergency_stop_active": self.emergency_stop_active,
            "total_active_faults": len(self.active_faults),
            "active_faults_by_level": {k: len(v) for k, v in active_by_level.items()},
            "fault_history_length": len(self.fault_history),
            "performance_metrics": self._get_performance_metrics()
        }
    
    def _get_performance_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics from recent history"""
        if len(self.position_error_history) < 5:
            return {"error_rms": 0.0, "velocity_rms": 0.0}
        
        errors = np.array(list(self.position_error_history))
        velocities = np.array(list(self.velocity_history))
        
        return {
            "error_rms": np.sqrt(np.mean(errors**2)),
            "error_max": np.max(errors),
            "velocity_rms": np.sqrt(np.mean(velocities**2)),
            "velocity_max": np.max(np.abs(velocities))
        }


class SystemSafetyManager:
    """
    System-wide safety management for multi-axis SIMPL automation system.
    Coordinates safety across all axes and manages system-level responses.
    """
    
    def __init__(self, axis_names: List[str]):
        self.axis_names = axis_names
        self.axis_monitors: Dict[str, SafetyMonitor] = {}
        
        # System-level safety state
        self.system_emergency_stop = False
        self.system_fault_callbacks: List[Callable] = []
        
        # Fault statistics
        self.total_faults_detected = 0
        self.fault_rate_window = deque(maxlen=100)  # Fault times for rate calculation
        
    def add_axis_monitor(self, axis_name: str, limits: SafetyLimits) -> SafetyMonitor:
        """Add safety monitor for an axis"""
        monitor = SafetyMonitor(axis_name, limits)
        monitor.set_emergency_stop_callback(self._axis_emergency_callback)
        self.axis_monitors[axis_name] = monitor
        return monitor
    
    def _axis_emergency_callback(self, fault: FaultEvent) -> None:
        """Callback when any axis triggers emergency stop"""
        self.system_emergency_stop = True
        
        # Notify all system fault callbacks
        for callback in self.system_fault_callbacks:
            callback(fault)
    
    def add_system_fault_callback(self, callback: Callable) -> None:
        """Add callback for system-level fault notifications"""
        self.system_fault_callbacks.append(callback)
    
    def update_all_axes(self, axis_states: Dict[str, Dict[str, float]]) -> Dict[str, List[FaultEvent]]:
        """
        Update safety monitoring for all axes.
        
        Args:
            axis_states: Dictionary with state data for each axis
                        Each axis should have: position, velocity, acceleration, 
                        current, setpoint, control_output
                        
        Returns:
            Dictionary of new faults detected per axis
        """
        all_new_faults = {}
        
        for axis_name, monitor in self.axis_monitors.items():
            if axis_name in axis_states:
                state = axis_states[axis_name]
                new_faults = monitor.update(
                    position=state.get('position', 0.0),
                    velocity=state.get('velocity', 0.0),
                    acceleration=state.get('acceleration', 0.0),
                    current=state.get('current', 0.0),
                    setpoint=state.get('setpoint', 0.0),
                    control_output=state.get('control_output', 0.0)
                )
                
                all_new_faults[axis_name] = new_faults
                
                # Update system statistics
                self.total_faults_detected += len(new_faults)
                for fault in new_faults:
                    self.fault_rate_window.append(fault.timestamp)
        
        return all_new_faults
    
    def system_emergency_stop(self, reason: str = "System emergency stop") -> None:
        """Trigger system-wide emergency stop"""
        self.system_emergency_stop = True
        
        # Trigger emergency stop on all axes
        for monitor in self.axis_monitors.values():
            monitor.emergency_stop(f"System E-Stop: {reason}")
    
    def reset_system_emergency_stop(self) -> bool:
        """Reset system emergency stop if all axes are safe"""
        if not self.system_emergency_stop:
            return True
        
        # Check if all axes can be reset
        all_safe = True
        for monitor in self.axis_monitors.values():
            if not monitor.reset_emergency_stop():
                all_safe = False
        
        if all_safe:
            self.system_emergency_stop = False
            return True
        
        return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system safety status"""
        axis_summaries = {}
        total_active_faults = 0
        highest_severity = SafetyLevel.INFO
        
        for axis_name, monitor in self.axis_monitors.items():
            summary = monitor.get_fault_summary()
            axis_summaries[axis_name] = summary
            total_active_faults += summary["total_active_faults"]
            
            # Find highest severity active fault
            active_faults = monitor.get_active_faults()
            for fault in active_faults:
                if fault.safety_level == SafetyLevel.EMERGENCY:
                    highest_severity = SafetyLevel.EMERGENCY
                elif fault.safety_level == SafetyLevel.CRITICAL and highest_severity != SafetyLevel.EMERGENCY:
                    highest_severity = SafetyLevel.CRITICAL
                elif fault.safety_level == SafetyLevel.WARNING and highest_severity == SafetyLevel.INFO:
                    highest_severity = SafetyLevel.WARNING
        
        # Calculate fault rate (faults per minute)
        current_time = time.time()
        recent_faults = [t for t in self.fault_rate_window if current_time - t < 60.0]
        fault_rate = len(recent_faults)  # Faults in last minute
        
        return {
            "system_emergency_stop": self.system_emergency_stop,
            "total_active_faults": total_active_faults,
            "highest_severity": highest_severity.value,
            "fault_rate_per_minute": fault_rate,
            "total_faults_detected": self.total_faults_detected,
            "axis_summaries": axis_summaries
        }
    
    def get_all_active_faults(self) -> List[FaultEvent]:
        """Get all active faults across all axes"""
        all_faults = []
        for monitor in self.axis_monitors.values():
            all_faults.extend(monitor.get_active_faults())
        return all_faults


def create_warehouse_safety_limits() -> Dict[str, SafetyLimits]:
    """Create typical safety limits for SIMPL warehouse axes"""
    return {
        'X': SafetyLimits(
            position_min=-5.0, position_max=5.0,
            velocity_max=3.0, acceleration_max=10.0,
            current_max=8.0, position_error_max=0.05
        ),
        'Y': SafetyLimits(
            position_min=-2.0, position_max=3.0,  # Vertical axis limits
            velocity_max=2.0, acceleration_max=8.0,
            current_max=12.0, position_error_max=0.03  # Tighter tolerance for gravity axis
        ),
        'Z': SafetyLimits(
            position_min=-3.0, position_max=3.0,
            velocity_max=2.5, acceleration_max=9.0,
            current_max=7.0, position_error_max=0.04
        )
    }


if __name__ == "__main__":
    # Test safety monitoring
    limits = SafetyLimits()
    monitor = SafetyMonitor("Test_Axis", limits)
    
    def emergency_callback(fault):
        print(f"EMERGENCY: {fault.message}")
    
    monitor.set_emergency_stop_callback(emergency_callback)
    
    print("Testing safety monitor...")
    
    # Test normal operation
    faults = monitor.update(position=1.0, velocity=0.5, acceleration=1.0,
                           current=2.0, setpoint=1.0, control_output=3.0)
    print(f"Normal operation faults: {len(faults)}")
    
    # Test position limit violation
    faults = monitor.update(position=15.0, velocity=0.5, acceleration=1.0,
                           current=2.0, setpoint=1.0, control_output=3.0)
    print(f"Position limit violation faults: {len(faults)}")
    for fault in faults:
        print(f"  {fault.fault_type.value}: {fault.message}")
    
    # Test system-wide monitoring
    print("\nTesting system safety manager...")
    manager = SystemSafetyManager(['X', 'Y', 'Z'])
    
    # Add monitors for each axis
    limits_dict = create_warehouse_safety_limits()
    for axis in ['X', 'Y', 'Z']:
        manager.add_axis_monitor(axis, limits_dict[axis])
    
    # Test normal operation
    axis_states = {
        'X': {'position': 1.0, 'velocity': 0.5, 'acceleration': 1.0,
              'current': 2.0, 'setpoint': 1.0, 'control_output': 3.0},
        'Y': {'position': 0.5, 'velocity': 0.2, 'acceleration': 0.5,
              'current': 3.0, 'setpoint': 0.5, 'control_output': 2.0},
        'Z': {'position': -1.0, 'velocity': -0.3, 'acceleration': -0.8,
              'current': 1.5, 'setpoint': -1.0, 'control_output': -1.0}
    }
    
    all_faults = manager.update_all_axes(axis_states)
    system_status = manager.get_system_status()
    
    print(f"System status: {system_status['total_active_faults']} active faults")
    print(f"Emergency stop: {system_status['system_emergency_stop']}")