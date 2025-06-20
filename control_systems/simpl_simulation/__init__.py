"""
SIMPL Automation Control Systems Simulation Package

This package provides a complete simulation of the SIMPL warehouse automation system
including servo motors, PID controllers, trajectory generation, safety monitoring,
and integrated motion control.

Main Components:
- servo_motor: Mathematical models of brushless servo motors
- pid_controller: Advanced PID controllers with anti-windup and gain scheduling
- trajectory_generator: S-curve trajectory generation for smooth motion
- safety_monitor: Comprehensive safety monitoring and fault detection
- motion_controller: Integrated multi-axis motion control
- warehouse_simulator: Complete warehouse operation simulation

Example Usage:
    from simpl_simulation import WarehouseSimulator
    
    # Create and run simulation
    warehouse = WarehouseSimulator()
    warehouse.run_simulation(duration=60.0)
"""

from .servo_motor import (
    ServoMotor, 
    MotorParameters,
    create_x_axis_motor,
    create_y_axis_motor, 
    create_z_axis_motor
)

from .pid_controller import (
    PIDController,
    PIDGains,
    PIDLimits,
    ControllerMode,
    create_position_controller,
    create_velocity_controller
)

from .trajectory_generator import (
    TrajectorySegment,
    MultiAxisTrajectory,
    MotionConstraints,
    TrajectoryType,
    Waypoint,
    create_warehouse_constraints,
    plot_trajectory_segment
)

from .safety_monitor import (
    SafetyMonitor,
    SystemSafetyManager,
    SafetyLimits,
    FaultEvent,
    FaultType,
    SafetyLevel,
    create_warehouse_safety_limits
)

from .motion_controller import (
    MotionController,
    AxisState,
    ControllerState
)

from .warehouse_simulator import (
    WarehouseSimulator,
    BinLocation,
    WarehouseTask,
    WarehouseTaskType
)

__version__ = "1.0.0"
__author__ = "SIMPL Automation Control Systems Team"

# Package metadata
__all__ = [
    # Servo Motor
    'ServoMotor', 'MotorParameters',
    'create_x_axis_motor', 'create_y_axis_motor', 'create_z_axis_motor',
    
    # PID Controller  
    'PIDController', 'PIDGains', 'PIDLimits', 'ControllerMode',
    'create_position_controller', 'create_velocity_controller',
    
    # Trajectory Generation
    'TrajectorySegment', 'MultiAxisTrajectory', 'MotionConstraints',
    'TrajectoryType', 'Waypoint', 'create_warehouse_constraints',
    'plot_trajectory_segment',
    
    # Safety Monitoring
    'SafetyMonitor', 'SystemSafetyManager', 'SafetyLimits',
    'FaultEvent', 'FaultType', 'SafetyLevel',
    'create_warehouse_safety_limits',
    
    # Motion Control
    'MotionController', 'AxisState', 'ControllerState',
    
    # Warehouse Simulation
    'WarehouseSimulator', 'BinLocation', 'WarehouseTask', 'WarehouseTaskType'
]