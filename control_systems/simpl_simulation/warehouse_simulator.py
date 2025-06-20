"""
Complete SIMPL Warehouse Automation System Simulator
Integrates all control system components for realistic warehouse operation simulation
"""

import numpy as np
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

from motion_controller import MotionController, ControllerState
from trajectory_generator import Waypoint
from safety_monitor import FaultEvent, SafetyLevel


class WarehouseTaskType(Enum):
    """Types of warehouse tasks"""
    PICK = "pick"
    PLACE = "place"
    MOVE = "move"
    HOME = "home"
    INSPECT = "inspect"


@dataclass
class BinLocation:
    """Warehouse bin location definition"""
    id: str
    x: float          # X position in meters
    y: float          # Y position in meters  
    z: float          # Z position in meters
    occupied: bool = False
    payload_weight: float = 0.0  # kg


@dataclass
class WarehouseTask:
    """Single warehouse operation task"""
    task_id: str
    task_type: WarehouseTaskType
    source_bin: Optional[str] = None
    target_bin: Optional[str] = None
    priority: int = 1  # 1=highest, 10=lowest
    payload_weight: float = 0.0
    timeout: float = 60.0  # Maximum time to complete (seconds)


class WarehouseSimulator:
    """
    Complete warehouse automation system simulator.
    
    Simulates SIMPL gantry system with:
    - Realistic warehouse layout with bin locations
    - Task queue management and execution
    - Payload handling and weight effects
    - Performance metrics and monitoring
    - Fault injection for testing
    """
    
    def __init__(self, warehouse_config: Optional[Dict] = None):
        # Initialize motion controller
        self.motion_controller = MotionController(['X', 'Y', 'Z'])
        
        # Warehouse layout
        self.bin_locations: Dict[str, BinLocation] = {}
        self.current_payload_weight = 0.0
        
        # Task management
        self.task_queue: List[WarehouseTask] = []
        self.active_task: Optional[WarehouseTask] = None
        self.completed_tasks: List[WarehouseTask] = []
        self.failed_tasks: List[WarehouseTask] = []
        
        # End effector simulation
        self.gripper_closed = False
        self.gripper_force = 0.0
        
        # Performance tracking
        self.start_time = time.time()
        self.total_picks = 0
        self.total_places = 0
        self.total_distance_traveled = 0.0
        self.total_task_time = 0.0
        
        # Fault injection for testing
        self.fault_injection_enabled = False
        self.injected_faults = []
        
        # Initialize warehouse layout
        self._create_default_warehouse_layout()
        
        # System state
        self.system_initialized = False
        self.last_position = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
        
    def _create_default_warehouse_layout(self) -> None:
        """Create a typical warehouse bin layout"""
        # 5x4 grid of bins, 2 levels high
        bin_spacing_x = 0.5  # meters
        bin_spacing_z = 0.4  # meters
        level_height = 1.0   # meters
        
        bin_id = 1
        for level in range(2):  # 2 levels
            y_pos = level * level_height + 0.5
            for row in range(4):  # 4 rows
                z_pos = row * bin_spacing_z
                for col in range(5):  # 5 columns
                    x_pos = col * bin_spacing_x
                    
                    bin_location = BinLocation(
                        id=f"BIN_{bin_id:03d}",
                        x=x_pos,
                        y=y_pos,
                        z=z_pos,
                        occupied=np.random.random() > 0.3,  # 70% occupancy
                        payload_weight=np.random.uniform(0.5, 5.0) if np.random.random() > 0.3 else 0.0
                    )
                    
                    self.bin_locations[bin_location.id] = bin_location
                    bin_id += 1
        
        print(f"Created warehouse layout with {len(self.bin_locations)} bin locations")
        occupied_bins = sum(1 for bin_loc in self.bin_locations.values() if bin_loc.occupied)
        print(f"Occupancy: {occupied_bins}/{len(self.bin_locations)} bins ({occupied_bins/len(self.bin_locations)*100:.1f}%)")
    
    def initialize_system(self) -> bool:
        """Initialize the warehouse automation system"""
        print("Initializing SIMPL Warehouse System...")
        
        # Enable motion controller
        if not self.motion_controller.enable_system():
            print("Failed to enable motion controller")
            return False
        
        # Home all axes
        print("Homing all axes...")
        if not self.motion_controller.home_all_axes():
            print("Failed to home axes")
            return False
        
        # Wait for homing to complete
        max_home_time = 10.0
        start_time = time.time()
        
        while not self.motion_controller.is_motion_complete():
            self.motion_controller.update()
            time.sleep(0.01)
            
            if time.time() - start_time > max_home_time:
                print("Homing timeout")
                return False
        
        self.system_initialized = True
        print("System initialization complete")
        return True
    
    def add_task(self, task: WarehouseTask) -> None:
        """Add task to the queue"""
        # Insert task in priority order
        inserted = False
        for i, existing_task in enumerate(self.task_queue):
            if task.priority < existing_task.priority:
                self.task_queue.insert(i, task)
                inserted = True
                break
        
        if not inserted:
            self.task_queue.append(task)
        
        print(f"Added task {task.task_id}: {task.task_type.value} (priority {task.priority})")
    
    def create_pick_task(self, task_id: str, source_bin: str, target_bin: str, priority: int = 5) -> Optional[WarehouseTask]:
        """Create a pick and place task"""
        if source_bin not in self.bin_locations or target_bin not in self.bin_locations:
            print(f"Invalid bin location: {source_bin} or {target_bin}")
            return None
        
        source = self.bin_locations[source_bin]
        target = self.bin_locations[target_bin]
        
        if not source.occupied:
            print(f"Source bin {source_bin} is empty")
            return None
        
        if target.occupied:
            print(f"Target bin {target_bin} is already occupied")
            return None
        
        task = WarehouseTask(
            task_id=task_id,
            task_type=WarehouseTaskType.PICK,
            source_bin=source_bin,
            target_bin=target_bin,
            priority=priority,
            payload_weight=source.payload_weight
        )
        
        return task
    
    def execute_next_task(self) -> bool:
        """Execute the next task in the queue"""
        if not self.system_initialized:
            print("System not initialized")
            return False
        
        if self.active_task is not None:
            print("Task already in progress")
            return False
        
        if not self.task_queue:
            print("No tasks in queue")
            return False
        
        # Get next task
        self.active_task = self.task_queue.pop(0)
        task_start_time = time.time()
        
        print(f"Starting task {self.active_task.task_id}: {self.active_task.task_type.value}")
        
        try:
            if self.active_task.task_type == WarehouseTaskType.PICK:
                success = self._execute_pick_task()
            elif self.active_task.task_type == WarehouseTaskType.MOVE:
                success = self._execute_move_task()
            elif self.active_task.task_type == WarehouseTaskType.HOME:
                success = self._execute_home_task()
            else:
                print(f"Unsupported task type: {self.active_task.task_type}")
                success = False
            
            # Record task completion
            task_time = time.time() - task_start_time
            self.total_task_time += task_time
            
            if success:
                self.completed_tasks.append(self.active_task)
                print(f"Task {self.active_task.task_id} completed in {task_time:.2f}s")
            else:
                self.failed_tasks.append(self.active_task)
                print(f"Task {self.active_task.task_id} failed after {task_time:.2f}s")
            
            self.active_task = None
            return success
            
        except Exception as e:
            print(f"Exception during task execution: {e}")
            self.failed_tasks.append(self.active_task)
            self.active_task = None
            return False
    
    def _execute_pick_task(self) -> bool:
        """Execute a pick and place task"""
        if not self.active_task or not self.active_task.source_bin or not self.active_task.target_bin:
            return False
        
        source = self.bin_locations[self.active_task.source_bin]
        target = self.bin_locations[self.active_task.target_bin]
        
        # Phase 1: Move to source bin
        print(f"Moving to source bin {source.id} at ({source.x:.2f}, {source.y:.2f}, {source.z:.2f})")
        if not self._move_to_position(source.x, source.y, source.z):
            return False
        
        # Phase 2: Pick payload
        print("Picking payload...")
        if not self._pick_payload(source):
            return False
        
        # Phase 3: Move to target bin
        print(f"Moving to target bin {target.id} at ({target.x:.2f}, {target.y:.2f}, {target.z:.2f})")
        if not self._move_to_position(target.x, target.y, target.z):
            return False
        
        # Phase 4: Place payload
        print("Placing payload...")
        if not self._place_payload(target):
            return False
        
        # Update bin states
        source.occupied = False
        source.payload_weight = 0.0
        target.occupied = True
        target.payload_weight = self.active_task.payload_weight
        
        self.total_picks += 1
        self.total_places += 1
        
        return True
    
    def _execute_move_task(self) -> bool:
        """Execute a simple move task"""
        # Move to a random bin location
        bin_id = np.random.choice(list(self.bin_locations.keys()))
        bin_loc = self.bin_locations[bin_id]
        
        print(f"Moving to bin {bin_id} at ({bin_loc.x:.2f}, {bin_loc.y:.2f}, {bin_loc.z:.2f})")
        return self._move_to_position(bin_loc.x, bin_loc.y, bin_loc.z)
    
    def _execute_home_task(self) -> bool:
        """Execute homing task"""
        print("Moving to home position")
        return self._move_to_position(0.0, 0.0, 0.0)
    
    def _move_to_position(self, x: float, y: float, z: float, timeout: float = 30.0) -> bool:
        """Move to specified position with timeout"""
        target_positions = {'X': x, 'Y': y, 'Z': z}
        
        # Calculate distance for performance tracking
        current_status = self.motion_controller.get_system_status()
        current_x = current_status['axes']['X']['position']
        current_y = current_status['axes']['Y']['position']
        current_z = current_status['axes']['Z']['position']
        
        distance = np.sqrt((x - current_x)**2 + (y - current_y)**2 + (z - current_z)**2)
        self.total_distance_traveled += distance
        
        # Start move
        if not self.motion_controller.start_coordinated_move(target_positions):
            print("Failed to start coordinated move")
            return False
        
        # Wait for completion
        start_time = time.time()
        while not self.motion_controller.is_motion_complete():
            self.motion_controller.update()
            
            # Check for faults
            status = self.motion_controller.get_system_status()
            if status['controller_state'] == 'fault' or status['controller_state'] == 'emergency_stop':
                print(f"Motion failed due to: {status['controller_state']}")
                return False
            
            # Check timeout
            if time.time() - start_time > timeout:
                print("Move timeout")
                return False
            
            # Small delay to prevent busy waiting
            time.sleep(0.001)
        
        return True
    
    def _pick_payload(self, source: BinLocation) -> bool:
        """Simulate picking payload from source bin"""
        # Simulate gripper operation
        self.gripper_closed = True
        self.gripper_force = min(source.payload_weight * 2.0, 10.0)  # Force proportional to weight
        
        # Update payload weight (affects Y-axis gravity compensation)
        self.current_payload_weight = source.payload_weight
        self._update_payload_compensation()
        
        # Simulate pick time
        time.sleep(0.1)
        
        # Check for pick faults
        if self.fault_injection_enabled and np.random.random() < 0.05:  # 5% pick failure rate
            print("Pick operation failed - gripper fault")
            return False
        
        return True
    
    def _place_payload(self, target: BinLocation) -> bool:
        """Simulate placing payload in target bin"""
        # Simulate place operation
        self.gripper_closed = False
        self.gripper_force = 0.0
        
        # Remove payload weight
        self.current_payload_weight = 0.0
        self._update_payload_compensation()
        
        # Simulate place time
        time.sleep(0.1)
        
        # Check for place faults
        if self.fault_injection_enabled and np.random.random() < 0.02:  # 2% place failure rate
            print("Place operation failed - positioning error")
            return False
        
        return True
    
    def _update_payload_compensation(self) -> None:
        """Update gravity compensation based on current payload"""
        # Update Y-axis gravity compensation
        base_gravity = 0.5  # Base system weight compensation
        payload_gravity = self.current_payload_weight * 0.1  # Payload contribution
        total_gravity = base_gravity + payload_gravity
        
        # Update motion controller feed-forward
        self.motion_controller.gravity_compensation['Y'] = total_gravity
        
        # Optionally adjust PID gains based on payload
        if self.current_payload_weight > 3.0:  # Heavy payload
            self.motion_controller.position_controllers['Y'].select_gain_schedule('heavy_payload')
        elif self.current_payload_weight < 1.0:  # Light payload
            self.motion_controller.position_controllers['Y'].select_gain_schedule('light_payload')
        else:
            self.motion_controller.position_controllers['Y'].select_gain_schedule('default')
    
    def run_simulation(self, duration: float = 60.0, task_interval: float = 10.0) -> None:
        """
        Run warehouse simulation for specified duration.
        
        Args:
            duration: Total simulation time (seconds)
            task_interval: Average time between new tasks (seconds)
        """
        if not self.system_initialized:
            if not self.initialize_system():
                print("Failed to initialize system")
                return
        
        print(f"Starting warehouse simulation for {duration:.1f} seconds...")
        
        simulation_start = time.time()
        last_task_time = 0.0
        
        while time.time() - simulation_start < duration:
            current_time = time.time() - simulation_start
            
            # Add new tasks periodically
            if current_time - last_task_time > task_interval and not self.active_task:
                self._generate_random_task()
                last_task_time = current_time
            
            # Execute tasks
            if not self.active_task and self.task_queue:
                self.execute_next_task()
            
            # Update motion controller
            self.motion_controller.update()
            
            # Inject faults occasionally for testing
            if self.fault_injection_enabled and np.random.random() < 0.001:  # 0.1% chance per update
                self._inject_random_fault()
            
            # Small delay
            time.sleep(0.01)
        
        print("Simulation complete")
        self._print_simulation_results()
    
    def _generate_random_task(self) -> None:
        """Generate a random warehouse task"""
        task_types = [WarehouseTaskType.PICK, WarehouseTaskType.MOVE, WarehouseTaskType.HOME]
        task_type = np.random.choice(task_types, p=[0.7, 0.2, 0.1])  # 70% pick tasks
        
        task_id = f"TASK_{len(self.completed_tasks) + len(self.failed_tasks) + len(self.task_queue) + 1:04d}"
        
        if task_type == WarehouseTaskType.PICK:
            # Find occupied source and empty target
            occupied_bins = [bid for bid, bin_loc in self.bin_locations.items() if bin_loc.occupied]
            empty_bins = [bid for bid, bin_loc in self.bin_locations.items() if not bin_loc.occupied]
            
            if occupied_bins and empty_bins:
                source_bin = np.random.choice(occupied_bins)
                target_bin = np.random.choice(empty_bins)
                priority = np.random.randint(1, 6)
                
                task = self.create_pick_task(task_id, source_bin, target_bin, priority)
                if task:
                    self.add_task(task)
        else:
            # Simple move or home task
            task = WarehouseTask(
                task_id=task_id,
                task_type=task_type,
                priority=np.random.randint(3, 8)
            )
            self.add_task(task)
    
    def _inject_random_fault(self) -> None:
        """Inject a random fault for testing"""
        fault_types = ['position_error', 'velocity_limit', 'current_spike']
        fault_type = np.random.choice(fault_types)
        
        if fault_type == 'position_error':
            # Inject position disturbance
            axis = np.random.choice(['X', 'Y', 'Z'])
            disturbance = np.random.uniform(-0.02, 0.02)
            motor = self.motion_controller.motors[axis]
            motor.set_external_disturbance(disturbance)
            print(f"Injected position disturbance on {axis}-axis: {disturbance:.4f}")
        
        # Record fault injection
        self.injected_faults.append({
            'time': time.time(),
            'type': fault_type,
            'axis': axis if 'axis' in locals() else 'system'
        })
    
    def enable_fault_injection(self, enabled: bool = True) -> None:
        """Enable/disable fault injection for testing"""
        self.fault_injection_enabled = enabled
        print(f"Fault injection {'enabled' if enabled else 'disabled'}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        runtime = time.time() - self.start_time
        
        # Task statistics
        total_tasks = len(self.completed_tasks) + len(self.failed_tasks)
        success_rate = len(self.completed_tasks) / total_tasks if total_tasks > 0 else 0.0
        
        # Throughput metrics
        picks_per_hour = self.total_picks / (runtime / 3600) if runtime > 0 else 0.0
        avg_task_time = self.total_task_time / len(self.completed_tasks) if self.completed_tasks else 0.0
        
        # Motion controller performance
        controller_status = self.motion_controller.get_system_status()
        
        return {
            'runtime_seconds': runtime,
            'total_tasks': total_tasks,
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'success_rate': success_rate,
            'total_picks': self.total_picks,
            'total_places': self.total_places,
            'picks_per_hour': picks_per_hour,
            'total_distance_traveled': self.total_distance_traveled,
            'average_task_time': avg_task_time,
            'current_payload_weight': self.current_payload_weight,
            'control_performance': {
                'max_cycle_time': controller_status['max_cycle_time'],
                'control_overruns': controller_status['control_overruns'],
                'emergency_stops': controller_status['safety']['system_emergency_stop']
            },
            'fault_injection': {
                'enabled': self.fault_injection_enabled,
                'total_faults_injected': len(self.injected_faults)
            }
        }
    
    def _print_simulation_results(self) -> None:
        """Print comprehensive simulation results"""
        metrics = self.get_performance_metrics()
        
        print("\n" + "="*60)
        print("SIMPL WAREHOUSE SIMULATION RESULTS")
        print("="*60)
        
        print(f"Runtime: {metrics['runtime_seconds']:.1f} seconds")
        print(f"Total Tasks: {metrics['total_tasks']}")
        print(f"Completed: {metrics['completed_tasks']}")
        print(f"Failed: {metrics['failed_tasks']}")
        print(f"Success Rate: {metrics['success_rate']:.1%}")
        
        print(f"\nThroughput:")
        print(f"Total Picks: {metrics['total_picks']}")
        print(f"Picks per Hour: {metrics['picks_per_hour']:.1f}")
        print(f"Average Task Time: {metrics['average_task_time']:.2f}s")
        print(f"Total Distance: {metrics['total_distance_traveled']:.2f}m")
        
        print(f"\nControl Performance:")
        print(f"Max Cycle Time: {metrics['control_performance']['max_cycle_time']:.4f}s")
        print(f"Control Overruns: {metrics['control_performance']['control_overruns']}")
        
        if self.fault_injection_enabled:
            print(f"\nFault Injection:")
            print(f"Total Faults Injected: {metrics['fault_injection']['total_faults_injected']}")
        
        print("="*60)
    
    def export_results(self, filename: str) -> None:
        """Export simulation results to JSON file"""
        results = {
            'performance_metrics': self.get_performance_metrics(),
            'bin_layout': {bid: {
                'x': bin_loc.x, 'y': bin_loc.y, 'z': bin_loc.z,
                'occupied': bin_loc.occupied, 'weight': bin_loc.payload_weight
            } for bid, bin_loc in self.bin_locations.items()},
            'completed_tasks': [{
                'task_id': task.task_id,
                'task_type': task.task_type.value,
                'source_bin': task.source_bin,
                'target_bin': task.target_bin,
                'payload_weight': task.payload_weight
            } for task in self.completed_tasks],
            'failed_tasks': [{
                'task_id': task.task_id,
                'task_type': task.task_type.value,
                'reason': 'execution_failed'
            } for task in self.failed_tasks]
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results exported to {filename}")


if __name__ == "__main__":
    # Create and run warehouse simulation
    print("SIMPL Warehouse Automation System Simulator")
    print("============================================")
    
    # Create simulator
    warehouse = WarehouseSimulator()
    
    # Enable fault injection for testing
    warehouse.enable_fault_injection(True)
    
    # Run simulation
    try:
        warehouse.run_simulation(duration=120.0, task_interval=15.0)  # 2 minutes, new task every 15s
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    
    # Export results
    warehouse.export_results('warehouse_simulation_results.json')