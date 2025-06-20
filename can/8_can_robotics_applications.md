# Lesson 8: CAN in Robotics Applications

## Why CAN for Robotics?

CAN bus offers unique advantages for robotics applications:

| Advantage | Robotics Benefit |
|-----------|------------------|
| **Distributed Control** | Multiple processors can control different subsystems |
| **Real-time Communication** | Deterministic response for motion control |
| **Robustness** | Immunity to electromagnetic interference from motors |
| **Scalability** | Easy to add sensors, actuators, and control nodes |
| **Reduced Wiring** | Simplified cable management in articulated arms |
| **Fault Tolerance** | System continues operation with failed nodes |

## Robotics System Architecture

### Traditional Centralized vs CAN-based Distributed

```mermaid
graph TD
    subgraph "Centralized Architecture"
        A[Main Controller] --> B[Motor Driver 1]
        A --> C[Motor Driver 2]
        A --> D[Motor Driver 3]
        A --> E[Sensor Interface 1]
        A --> F[Sensor Interface 2]
        A --> G[I/O Interface]
    end
    
    subgraph "CAN-based Distributed Architecture"
        H[CAN Bus] --> I[Motor Node 1]
        H --> J[Motor Node 2]
        H --> K[Motor Node 3]
        H --> L[Sensor Node 1]
        H --> M[Sensor Node 2]
        H --> N[I/O Node]
        H --> O[Main Controller]
    end
    
    style H fill:#e1f5fe
    style O fill:#c8e6c9
```

## Robotic System Components

### CAN-enabled Robotic Components

```mermaid
mindmap
  root((Robotic CAN Network))
    Motion Control
      Servo Motors
      Stepper Motors
      Linear Actuators
      Pneumatic Valves
    Sensing
      Encoders
      Force/Torque Sensors
      Vision Systems
      Proximity Sensors
      IMU Sensors
    Control
      Joint Controllers
      Master Controller
      Safety Controller
      HMI Interface
    I/O Systems
      Digital I/O
      Analog I/O
      Fieldbus Gateways
      Wireless Interfaces
```

## Multi-Axis Robot Control

### 6-DOF Robotic Arm Example

```mermaid
graph TD
    A[Master Controller<br/>Motion Planning] --> B[CAN Bus]
    
    B --> C[Joint 1 Controller<br/>Shoulder Yaw]
    B --> D[Joint 2 Controller<br/>Shoulder Pitch]
    B --> E[Joint 3 Controller<br/>Elbow]
    B --> F[Joint 4 Controller<br/>Wrist Roll]
    B --> G[Joint 5 Controller<br/>Wrist Pitch]
    B --> H[Joint 6 Controller<br/>Wrist Yaw]
    
    B --> I[Gripper Controller]
    B --> J[Force/Torque Sensor]
    B --> K[Safety Controller]
    
    style A fill:#e1f5fe
    style B fill:#c8e6c9
    style K fill:#ffcdd2
```

### Real-time Motion Coordination

```mermaid
sequenceDiagram
    participant MC as Master Controller
    participant J1 as Joint 1
    participant J2 as Joint 2
    participant J3 as Joint 3
    participant J4 as Joint 4
    participant J5 as Joint 5
    participant J6 as Joint 6
    
    MC->>J1: SYNC Signal
    MC->>J2: SYNC Signal
    MC->>J3: SYNC Signal
    MC->>J4: SYNC Signal
    MC->>J5: SYNC Signal
    MC->>J6: SYNC Signal
    
    Note over J1,J6: Synchronized position updates
    
    J1->>MC: Position Feedback
    J2->>MC: Position Feedback
    J3->>MC: Position Feedback
    J4->>MC: Position Feedback
    J5->>MC: Position Feedback
    J6->>MC: Position Feedback
    
    MC->>J1: Next Position Command
    MC->>J2: Next Position Command
    MC->>J3: Next Position Command
    MC->>J4: Next Position Command
    MC->>J5: Next Position Command
    MC->>J6: Next Position Command
```

## CANopen for Motor Control

### Motor Control Profile (CiA 402)

```mermaid
graph TD
    A[Motor Control State Machine] --> B[Switch On Disabled]
    B --> C[Ready to Switch On]
    C --> D[Switched On]
    D --> E[Operation Enable]
    
    E --> F[Quick Stop Active]
    F --> G[Fault Reaction Active]
    G --> H[Fault]
    
    I[Control Word] --> J[Bit 0: Switch On<br/>Bit 1: Enable Voltage<br/>Bit 2: Quick Stop<br/>Bit 3: Enable Operation]
    
    K[Status Word] --> L[Bit 0: Ready to Switch On<br/>Bit 1: Switched On<br/>Bit 2: Operation Enable<br/>Bit 3: Fault]
    
    style E fill:#c8e6c9
    style H fill:#ffcdd2
```

### Motion Control Modes

| Mode | Code | Description | Use Case |
|------|------|-------------|----------|
| **Profile Position** | 1 | Absolute/relative positioning | Point-to-point motion |
| **Profile Velocity** | 3 | Velocity control with ramps | Conveyor systems |
| **Profile Torque** | 4 | Torque/force control | Assembly operations |
| **Homing** | 6 | Reference position finding | Calibration |
| **Interpolated Position** | 7 | Synchronized motion | Coordinated multi-axis |
| **Cyclic Synchronous Position** | 8 | Real-time position control | Servo control |
| **Cyclic Synchronous Velocity** | 9 | Real-time velocity control | Speed control |
| **Cyclic Synchronous Torque** | 10 | Real-time torque control | Force control |

## Sensor Integration

### Distributed Sensor Network

```mermaid
graph LR
    A[CAN Bus] --> B[Vision System<br/>Object Detection]
    A --> C[Force/Torque Sensor<br/>Contact Forces]
    A --> D[Proximity Sensors<br/>Collision Avoidance]
    A --> E[Temperature Sensors<br/>Thermal Monitoring]
    A --> F[Accelerometer<br/>Vibration Analysis]
    A --> G[Encoder Feedback<br/>Position Accuracy]
    
    B --> H[CANopen Device<br/>Profile CiA 404]
    C --> I[Custom Profile<br/>High-speed Data]
    D --> J[I/O Profile<br/>CiA 401]
    
    style A fill:#e1f5fe
    style H fill:#c8e6c9
    style I fill:#fff3e0
    style J fill:#e8f5e8
```

### High-Speed Sensor Data

For high-frequency sensor data, optimize PDO configuration:

```c
// Example: 1 kHz force sensor data
typedef struct {
    uint32_t pdo_id;           // 0x180 + node_id
    uint8_t  transmission_type; // 254 (asynchronous)
    uint16_t inhibit_time;     // 10 (1ms minimum)
    uint16_t event_timer;      // 10 (1ms periodic)
} force_sensor_pdo_t;

// Sensor data mapping
typedef struct {
    int16_t force_x;    // 2 bytes
    int16_t force_y;    // 2 bytes  
    int16_t force_z;    // 2 bytes
    int16_t torque_x;   // 2 bytes
    // Total: 8 bytes (full PDO)
} force_data_t;
```

## Safety Systems

### Functional Safety with CAN

```mermaid
graph TD
    A[Safety System Architecture] --> B[Safety Controller]
    A --> C[Safety Sensors]
    A --> D[Safety Actuators]
    
    B --> E[Emergency Stop Processing<br/>Safety Logic<br/>Diagnostics]
    
    C --> F[Light Curtains<br/>Pressure Mats<br/>Enable Switches<br/>Position Monitors]
    
    D --> G[Safety Relays<br/>Safe Torque Off<br/>Brake Control<br/>Valve Control]
    
    H[Safety CAN Network] --> B
    H --> C
    H --> D
    
    style H fill:#ffcdd2
    style E fill:#fff3e0
```

### Safety Message Priorities

| Priority | CAN ID Range | Message Type | Response Time |
|----------|--------------|--------------|---------------|
| **Emergency Stop** | 0x080-0x0FF | Immediate halt | < 1ms |
| **Safety Monitoring** | 0x100-0x17F | Status updates | < 10ms |
| **Safety Configuration** | 0x180-0x1FF | Parameter changes | < 100ms |
| **Diagnostics** | 0x700-0x77F | Error reporting | < 1s |

## Mobile Robot Applications

### Autonomous Mobile Robot (AMR)

```mermaid
graph TD
    A[Main Controller<br/>Navigation & Planning] --> B[CAN Bus]
    
    B --> C[Drive Controller<br/>Left Wheel]
    B --> D[Drive Controller<br/>Right Wheel]
    B --> E[Steering Controller<br/>Front Wheels]
    
    B --> F[LiDAR Interface<br/>Obstacle Detection]
    B --> G[Camera Interface<br/>Vision Processing]
    B --> H[IMU Sensor<br/>Orientation]
    
    B --> I[Battery Management<br/>Power Monitoring]
    B --> J[Charging Interface<br/>Docking Control]
    B --> K[Payload Interface<br/>Cargo Handling]
    
    style A fill:#e1f5fe
    style B fill:#c8e6c9
```

### Differential Drive Control

```c
// Example: Differential drive mobile robot
typedef struct {
    // Motion commands
    float linear_velocity;     // m/s
    float angular_velocity;    // rad/s
    
    // Wheel speeds (calculated)
    float left_wheel_speed;    // rad/s
    float right_wheel_speed;   // rad/s
    
    // Feedback
    float actual_linear_vel;   // m/s
    float actual_angular_vel;  // rad/s
    
    // Robot parameters
    float wheel_base;          // m
    float wheel_radius;        // m
} differential_drive_t;

// CANopen PDO mapping for drive control
typedef struct {
    int16_t left_speed_cmd;    // Left wheel speed command
    int16_t right_speed_cmd;   // Right wheel speed command
    uint16_t control_word;     // Drive control word
    uint16_t status_word;      // Drive status word
} drive_pdo_t;
```

## Collaborative Robotics (Cobots)

### Human-Robot Interaction

```mermaid
graph TD
    A[Collaborative Robot System] --> B[Force Sensing]
    A --> C[Vision System]
    A --> D[Safety Monitoring]
    A --> E[Adaptive Control]
    
    B --> F[Joint Torque Sensors<br/>External Force Detection<br/>Collision Detection]
    
    C --> G[Human Detection<br/>Workspace Monitoring<br/>Intent Recognition]
    
    D --> H[Speed Monitoring<br/>Power Limiting<br/>Stop Category 0/1/2]
    
    E --> I[Impedance Control<br/>Compliant Motion<br/>Dynamic Reconfiguration]
    
    J[CAN Network] --> B
    J --> C
    J --> D
    J --> E
    
    style J fill:#e1f5fe
    style F fill:#c8e6c9
    style H fill:#ffcdd2
```

### Real-time Force Control

```c
// Example: Impedance control for collaborative robot
typedef struct {
    // Force/torque feedback
    float force_x, force_y, force_z;        // N
    float torque_x, torque_y, torque_z;     // Nm
    
    // Impedance parameters
    float stiffness[6];                     // N/m, Nm/rad
    float damping[6];                       // Ns/m, Nms/rad
    float mass[6];                          // kg, kg*m²
    
    // Control output
    float position_correction[6];           // m, rad
    float velocity_correction[6];           // m/s, rad/s
} impedance_control_t;

// High-speed CAN-FD PDO for force control
// 1 kHz update rate, 32 bytes payload
typedef struct {
    float force_xyz[3];        // 12 bytes
    float torque_xyz[3];       // 12 bytes
    uint32_t timestamp;        // 4 bytes
    uint16_t status;           // 2 bytes
    uint16_t reserved;         // 2 bytes
} force_control_pdo_t;
```

## Industrial Robot Integration

### Factory Automation Integration

```mermaid
graph LR
    A[Factory Network] --> B[Industrial Ethernet]
    B --> C[CAN Gateway]
    C --> D[Robot CAN Network]
    
    D --> E[Robot Controller]
    D --> F[Gripper Controller]
    D --> G[Conveyor Interface]
    D --> H[Quality Control]
    D --> I[Parts Feeder]
    
    J[MES/ERP System] --> A
    K[HMI/SCADA] --> A
    L[Safety System] --> D
    
    style D fill:#e1f5fe
    style L fill:#ffcdd2
```

### Production Line Coordination

```mermaid
sequenceDiagram
    participant PLC as Factory PLC
    participant RC as Robot Controller
    participant GC as Gripper Controller
    participant CV as Conveyor
    participant QC as Quality Control
    
    PLC->>RC: Start Production Cycle
    RC->>CV: Request Part Position
    CV->>RC: Part Ready at Position X
    
    RC->>GC: Move to Pick Position
    GC->>RC: Position Reached
    RC->>GC: Close Gripper
    GC->>RC: Part Grasped
    
    RC->>RC: Move to Assembly Position
    RC->>GC: Place Part
    GC->>RC: Part Placed
    
    RC->>QC: Trigger Quality Check
    QC->>RC: Quality OK/NOK
    RC->>PLC: Cycle Complete
```

## Advantages of CAN in Robotics

### Performance Benefits

| Aspect | Traditional | CAN-based | Improvement |
|--------|-------------|-----------|-------------|
| **Wiring Complexity** | N × M connections | Single bus | 90% reduction |
| **EMI Immunity** | Susceptible | Differential signaling | High immunity |
| **Fault Tolerance** | Single point failure | Distributed | Graceful degradation |
| **Scalability** | Fixed I/O | Dynamic nodes | Easy expansion |
| **Real-time Response** | Variable | Deterministic | Predictable timing |
| **Diagnostics** | Limited | Comprehensive | Full visibility |

### Cost Analysis

```mermaid
graph TD
    A[Cost Comparison] --> B[Traditional System]
    A --> C[CAN-based System]
    
    B --> D[High cable costs<br/>Complex harnesses<br/>Centralized I/O<br/>Single controller]
    
    C --> E[Reduced cabling<br/>Distributed intelligence<br/>Modular design<br/>Easier maintenance]
    
    F[Initial Cost] --> G[CAN: +20%<br/>Additional controllers]
    H[Operating Cost] --> I[CAN: -40%<br/>Reduced maintenance]
    J[Lifecycle Cost] --> K[CAN: -25%<br/>Better flexibility]
    
    style C fill:#c8e6c9
    style D fill:#ffcdd2
```

## Implementation Challenges

### Common Robotics CAN Challenges

| Challenge | Solution | Implementation |
|-----------|----------|----------------|
| **Synchronization** | SYNC master with GPS/PTP | Network-wide time base |
| **Bandwidth Limitations** | CAN-FD for high-speed data | Selective upgrade |
| **Cable Management** | Proper routing and protection | Flexible cable chains |
| **EMI from Motors** | Shielded cables and grounding | Proper installation |
| **Safety Integration** | Dedicated safety networks | Dual-channel architecture |
| **Deterministic Timing** | Priority-based message design | Careful ID allocation |

## Design Guidelines for Robotic CAN

### Network Architecture Best Practices

```mermaid
graph TD
    A[Robotic CAN Design] --> B[Hierarchical Structure]
    A --> C[Message Prioritization]
    A --> D[Redundancy Planning]
    A --> E[Timing Analysis]
    
    B --> F[Motion Control: High Priority<br/>Sensors: Medium Priority<br/>Diagnostics: Low Priority]
    
    C --> G[Emergency: 0x000-0x0FF<br/>Motion: 0x100-0x2FF<br/>Sensors: 0x300-0x4FF<br/>Status: 0x500-0x7FF]
    
    D --> H[Dual CAN buses<br/>Backup controllers<br/>Fail-safe mechanisms]
    
    E --> I[Worst-case analysis<br/>Jitter calculation<br/>Bandwidth utilization]
    
    style A fill:#e1f5fe
```

## Learning Objectives Achieved

- ✅ Understand CAN advantages for robotics applications
- ✅ Know distributed control architectures for robots
- ✅ Understand multi-axis motion control coordination
- ✅ Recognize sensor integration strategies
- ✅ Know safety system implementation with CAN
- ✅ Understand mobile robot and cobot applications

## Next Steps

In [Lesson 9: CAN Network Design and Implementation](9_can_network_design.md), we'll cover the practical aspects of designing, implementing, and optimizing CAN networks for real-world applications.

## Practical Exercises

1. Design CAN network for 6-DOF robotic arm with force feedback
2. Calculate timing requirements for 10-axis synchronized motion
3. Implement safety system with emergency stop propagation
4. Design mobile robot navigation with CAN-based sensor fusion
5. Create collaborative robot force control system using CAN-FD