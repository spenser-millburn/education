"""
Trajectory Generation for SIMPL Automation System
Implements smooth, jerk-limited motion profiles for warehouse automation
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt


class TrajectoryType(Enum):
    """Types of trajectory profiles"""
    TRAPEZOIDAL = "trapezoidal"
    S_CURVE = "s_curve"
    POINT_TO_POINT = "point_to_point"
    CONTINUOUS_PATH = "continuous_path"


@dataclass
class MotionConstraints:
    """Motion constraints for trajectory generation"""
    max_velocity: float = 1.0        # rad/s or m/s
    max_acceleration: float = 2.0    # rad/s² or m/s²
    max_jerk: float = 10.0          # rad/s³ or m/s³
    
    def __post_init__(self):
        """Validate constraints are positive"""
        if any(x <= 0 for x in [self.max_velocity, self.max_acceleration, self.max_jerk]):
            raise ValueError("Motion constraints must be positive")


@dataclass
class Waypoint:
    """Single waypoint in a trajectory"""
    position: float
    velocity: float = 0.0    # Desired velocity at waypoint (0 = stop)
    time: Optional[float] = None  # Optional time constraint
    
    
class TrajectorySegment:
    """
    Single trajectory segment with position, velocity, and acceleration profiles.
    Represents motion between two waypoints.
    """
    
    def __init__(self, start_pos: float, end_pos: float, constraints: MotionConstraints,
                 start_vel: float = 0.0, end_vel: float = 0.0):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.start_vel = start_vel
        self.end_vel = end_vel
        self.constraints = constraints
        
        # Calculate trajectory parameters
        self.distance = end_pos - start_pos
        self.direction = np.sign(self.distance) if self.distance != 0 else 1.0
        self.distance_abs = abs(self.distance)
        
        # Trajectory timing
        self.total_time = 0.0
        self.accel_time = 0.0
        self.coast_time = 0.0
        self.decel_time = 0.0
        self.jerk_time = 0.0  # For S-curve profiles
        
        # Profile type
        self.profile_type = TrajectoryType.S_CURVE
        
        # Calculate trajectory
        self._calculate_s_curve_profile()
        
    def _calculate_s_curve_profile(self) -> None:
        """Calculate S-curve (jerk-limited) trajectory profile"""
        max_vel = self.constraints.max_velocity
        max_accel = self.constraints.max_acceleration
        max_jerk = self.constraints.max_jerk
        
        # Time to reach maximum acceleration
        t_jerk = max_accel / max_jerk
        
        # Velocity gained during jerk phase
        v_jerk = 0.5 * max_accel * t_jerk
        
        # Distance covered during acceleration phase (with jerk)
        s_jerk = (1/6) * max_jerk * t_jerk**3
        
        # Check if we can reach maximum velocity
        # Distance needed to accelerate to max_vel
        if 2 * v_jerk >= max_vel:
            # Cannot reach max acceleration - triangle profile
            t_jerk_actual = np.sqrt(max_vel / max_jerk)
            t_accel = 2 * t_jerk_actual
            s_accel = max_vel * t_jerk_actual
            peak_velocity = max_vel
        else:
            # Can reach max acceleration
            t_accel_const = (max_vel - 2 * v_jerk) / max_accel
            t_accel = 2 * t_jerk + t_accel_const
            s_accel = 2 * s_jerk + v_jerk * t_accel_const + 0.5 * max_accel * t_accel_const**2
            peak_velocity = max_vel
        
        # Check if we have enough distance for full acceleration + deceleration
        s_total_accel_decel = 2 * s_accel  # Symmetric profile
        
        if s_total_accel_decel >= self.distance_abs:
            # No constant velocity phase - reduce peak velocity
            # Solve for peak velocity with available distance
            peak_velocity = np.sqrt(self.distance_abs * max_accel)
            peak_velocity = min(peak_velocity, max_vel)
            
            # Recalculate acceleration phase
            if 2 * v_jerk >= peak_velocity:
                t_jerk_actual = np.sqrt(peak_velocity / max_jerk)
                self.accel_time = 2 * t_jerk_actual
                self.coast_time = 0.0
            else:
                t_accel_const = (peak_velocity - 2 * v_jerk) / max_accel
                self.accel_time = 2 * t_jerk + t_accel_const
                self.coast_time = 0.0
        else:
            # Constant velocity phase exists
            self.accel_time = t_accel
            self.coast_time = (self.distance_abs - s_total_accel_decel) / peak_velocity
        
        self.decel_time = self.accel_time  # Symmetric
        self.jerk_time = t_jerk
        self.peak_velocity = peak_velocity * self.direction
        self.total_time = self.accel_time + self.coast_time + self.decel_time
        
    def evaluate(self, t: float) -> Tuple[float, float, float]:
        """
        Evaluate trajectory at given time.
        
        Args:
            t: Time since start of segment
            
        Returns:
            Tuple of (position, velocity, acceleration)
        """
        if t <= 0:
            return (self.start_pos, self.start_vel, 0.0)
        elif t >= self.total_time:
            return (self.end_pos, self.end_vel, 0.0)
        
        # Determine which phase we're in
        if t <= self.accel_time:
            return self._evaluate_acceleration_phase(t)
        elif t <= self.accel_time + self.coast_time:
            return self._evaluate_coast_phase(t - self.accel_time)
        else:
            return self._evaluate_deceleration_phase(t - self.accel_time - self.coast_time)
    
    def _evaluate_acceleration_phase(self, t: float) -> Tuple[float, float, float]:
        """Evaluate S-curve acceleration phase"""
        t_jerk = self.jerk_time
        max_accel = self.constraints.max_acceleration
        max_jerk = self.constraints.max_jerk
        
        if t <= t_jerk:
            # Increasing acceleration (jerk phase)
            jerk = max_jerk * self.direction
            accel = jerk * t
            vel = self.start_vel + 0.5 * jerk * t**2
            pos = self.start_pos + self.start_vel * t + (1/6) * jerk * t**3
        elif t <= self.accel_time - t_jerk:
            # Constant acceleration phase
            t_const = t - t_jerk
            jerk = 0.0
            accel = max_accel * self.direction
            vel_jerk = self.start_vel + 0.5 * max_jerk * self.direction * t_jerk**2
            vel = vel_jerk + accel * t_const
            pos_jerk = self.start_pos + self.start_vel * t_jerk + (1/6) * max_jerk * self.direction * t_jerk**3
            pos = pos_jerk + vel_jerk * t_const + 0.5 * accel * t_const**2
        else:
            # Decreasing acceleration (jerk phase)
            t_jerk2 = t - (self.accel_time - t_jerk)
            jerk = -max_jerk * self.direction
            accel = max_accel * self.direction - max_jerk * self.direction * t_jerk2
            
            # Calculate from start of this jerk phase
            vel_start = self.start_vel + 0.5 * max_jerk * self.direction * t_jerk**2 + max_accel * self.direction * (self.accel_time - 2*t_jerk)
            pos_start = (self.start_pos + self.start_vel * (self.accel_time - t_jerk) + 
                        (1/6) * max_jerk * self.direction * t_jerk**3 + 
                        vel_start * (self.accel_time - 2*t_jerk) + 
                        0.5 * max_accel * self.direction * (self.accel_time - 2*t_jerk)**2)
            
            vel = vel_start + max_accel * self.direction * t_jerk2 - 0.5 * max_jerk * self.direction * t_jerk2**2
            pos = pos_start + vel_start * t_jerk2 + 0.5 * max_accel * self.direction * t_jerk2**2 - (1/6) * max_jerk * self.direction * t_jerk2**3
        
        return (pos, vel, accel)
    
    def _evaluate_coast_phase(self, t: float) -> Tuple[float, float, float]:
        """Evaluate constant velocity phase"""
        vel = self.peak_velocity
        accel = 0.0
        pos = self.start_pos + self.distance_abs * (self.accel_time / self.total_time) + vel * t
        return (pos, vel, accel)
    
    def _evaluate_deceleration_phase(self, t: float) -> Tuple[float, float, float]:
        """Evaluate S-curve deceleration phase (mirror of acceleration)"""
        # Mirror the acceleration phase
        t_mirror = self.decel_time - t
        pos_mirror, vel_mirror, accel_mirror = self._evaluate_acceleration_phase(t_mirror)
        
        # Transform to deceleration phase
        pos = self.end_pos - (pos_mirror - self.start_pos)
        vel = -vel_mirror + 2 * self.end_vel
        accel = -accel_mirror
        
        return (pos, vel, accel)


class MultiAxisTrajectory:
    """
    Multi-axis trajectory generator for coordinated motion.
    Synchronizes multiple axes to reach targets simultaneously.
    """
    
    def __init__(self, axis_names: List[str], constraints: Dict[str, MotionConstraints]):
        self.axis_names = axis_names
        self.constraints = constraints
        self.segments = {}  # Current trajectory segments for each axis
        self.current_time = 0.0
        self.total_time = 0.0
        self.is_active = False
        
    def generate_coordinated_move(self, start_positions: Dict[str, float], 
                                end_positions: Dict[str, float],
                                start_velocities: Optional[Dict[str, float]] = None,
                                end_velocities: Optional[Dict[str, float]] = None) -> None:
        """
        Generate coordinated trajectory for multiple axes.
        All axes will complete motion at the same time.
        
        Args:
            start_positions: Starting position for each axis
            end_positions: Target position for each axis
            start_velocities: Optional starting velocities
            end_velocities: Optional ending velocities
        """
        if start_velocities is None:
            start_velocities = {axis: 0.0 for axis in self.axis_names}
        if end_velocities is None:
            end_velocities = {axis: 0.0 for axis in self.axis_names}
        
        # Generate individual segments
        individual_segments = {}
        individual_times = {}
        
        for axis in self.axis_names:
            if axis not in self.constraints:
                raise ValueError(f"No constraints defined for axis {axis}")
            
            start_pos = start_positions.get(axis, 0.0)
            end_pos = end_positions.get(axis, 0.0)
            start_vel = start_velocities.get(axis, 0.0)
            end_vel = end_velocities.get(axis, 0.0)
            
            segment = TrajectorySegment(start_pos, end_pos, self.constraints[axis],
                                      start_vel, end_vel)
            individual_segments[axis] = segment
            individual_times[axis] = segment.total_time
        
        # Find the longest time (limiting axis)
        self.total_time = max(individual_times.values()) if individual_times else 0.0
        
        # Scale all trajectories to match the longest time
        for axis in self.axis_names:
            segment = individual_segments[axis]
            if segment.total_time < self.total_time and segment.distance_abs > 1e-6:
                # Need to slow down this axis
                self._rescale_segment_for_time(segment, self.total_time)
            
            self.segments[axis] = segment
        
        self.current_time = 0.0
        self.is_active = True
    
    def _rescale_segment_for_time(self, segment: TrajectorySegment, target_time: float) -> None:
        """Rescale a trajectory segment to match target time"""
        if target_time <= segment.total_time:
            return  # No scaling needed
        
        # Simple approach: reduce peak velocity to stretch time
        time_ratio = segment.total_time / target_time
        segment.peak_velocity *= time_ratio
        
        # Recalculate timing with reduced velocity
        # This is a simplified approach - more sophisticated methods could maintain S-curve shape
        new_constraints = MotionConstraints(
            max_velocity=abs(segment.peak_velocity),
            max_acceleration=segment.constraints.max_acceleration * time_ratio,
            max_jerk=segment.constraints.max_jerk * time_ratio**2
        )
        
        # Recreate segment with new constraints
        new_segment = TrajectorySegment(
            segment.start_pos, segment.end_pos, new_constraints,
            segment.start_vel, segment.end_vel
        )
        
        # Copy calculated values
        segment.peak_velocity = new_segment.peak_velocity
        segment.total_time = new_segment.total_time
        segment.accel_time = new_segment.accel_time
        segment.coast_time = new_segment.coast_time
        segment.decel_time = new_segment.decel_time
        segment.jerk_time = new_segment.jerk_time
    
    def update(self, dt: float) -> Dict[str, Tuple[float, float, float]]:
        """
        Update trajectory and return current setpoints for all axes.
        
        Args:
            dt: Time step
            
        Returns:
            Dictionary with (position, velocity, acceleration) for each axis
        """
        if not self.is_active:
            return {axis: (0.0, 0.0, 0.0) for axis in self.axis_names}
        
        self.current_time += dt
        
        setpoints = {}
        for axis in self.axis_names:
            if axis in self.segments:
                setpoints[axis] = self.segments[axis].evaluate(self.current_time)
            else:
                setpoints[axis] = (0.0, 0.0, 0.0)
        
        # Check if trajectory is complete
        if self.current_time >= self.total_time:
            self.is_active = False
        
        return setpoints
    
    def is_complete(self) -> bool:
        """Check if trajectory is complete"""
        return not self.is_active
    
    def get_progress(self) -> float:
        """Get trajectory completion progress (0.0 to 1.0)"""
        if self.total_time <= 0:
            return 1.0
        return min(self.current_time / self.total_time, 1.0)
    
    def stop(self) -> None:
        """Stop trajectory execution"""
        self.is_active = False
    
    def get_total_time(self) -> float:
        """Get total trajectory time"""
        return self.total_time


def create_warehouse_constraints() -> Dict[str, MotionConstraints]:
    """Create typical motion constraints for SIMPL warehouse axes"""
    return {
        'X': MotionConstraints(max_velocity=2.0, max_acceleration=3.0, max_jerk=15.0),
        'Y': MotionConstraints(max_velocity=1.5, max_acceleration=2.0, max_jerk=10.0),  # Slower for vertical
        'Z': MotionConstraints(max_velocity=1.8, max_acceleration=2.5, max_jerk=12.0)
    }


def plot_trajectory_segment(segment: TrajectorySegment, dt: float = 0.001) -> None:
    """Plot position, velocity, and acceleration profiles for a trajectory segment"""
    times = np.arange(0, segment.total_time + dt, dt)
    positions = []
    velocities = []
    accelerations = []
    
    for t in times:
        pos, vel, acc = segment.evaluate(t)
        positions.append(pos)
        velocities.append(vel)
        accelerations.append(acc)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
    
    ax1.plot(times, positions)
    ax1.set_ylabel('Position')
    ax1.set_title('S-Curve Trajectory Profile')
    ax1.grid(True)
    
    ax2.plot(times, velocities)
    ax2.set_ylabel('Velocity')
    ax2.grid(True)
    
    ax3.plot(times, accelerations)
    ax3.set_ylabel('Acceleration')
    ax3.set_xlabel('Time (s)')
    ax3.grid(True)
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Test trajectory generation
    constraints = MotionConstraints(max_velocity=1.0, max_acceleration=2.0, max_jerk=10.0)
    segment = TrajectorySegment(0.0, 5.0, constraints)
    
    print(f"Trajectory from 0 to 5 units:")
    print(f"Total time: {segment.total_time:.3f} s")
    print(f"Peak velocity: {segment.peak_velocity:.3f}")
    print(f"Accel time: {segment.accel_time:.3f} s")
    print(f"Coast time: {segment.coast_time:.3f} s")
    print(f"Decel time: {segment.decel_time:.3f} s")
    
    # Test multi-axis coordination
    multi_traj = MultiAxisTrajectory(['X', 'Y', 'Z'], create_warehouse_constraints())
    
    start_pos = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
    end_pos = {'X': 2.0, 'Y': 1.0, 'Z': 0.5}
    
    multi_traj.generate_coordinated_move(start_pos, end_pos)
    print(f"\nMulti-axis trajectory time: {multi_traj.get_total_time():.3f} s")
    
    # Simulate first few time steps
    dt = 0.01
    for i in range(5):
        setpoints = multi_traj.update(dt)
        print(f"t={i*dt:.3f}: X={setpoints['X'][0]:.3f}, Y={setpoints['Y'][0]:.3f}, Z={setpoints['Z'][0]:.3f}")