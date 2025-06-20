# Lesson 7: CANopen Object Dictionary and Communication

## Object Dictionary Deep Dive

The Object Dictionary (OD) is CANopen's core data structure - a standardized database that defines how devices expose their functionality, configuration, and status information.

## Object Dictionary Structure

### Memory Map Overview

```mermaid
graph TD
    A[Object Dictionary<br/>0x0000-0xFFFF] --> B[Data Types<br/>0x0001-0x001F]
    A --> C[Communication Area<br/>0x1000-0x1FFF]  
    A --> D[Manufacturer Area<br/>0x2000-0x5FFF]
    A --> E[Standardized Area<br/>0x6000-0x9FFF]
    A --> F[Reserved<br/>0xA000-0xFFFF]
    
    C --> G[Device Information<br/>Identity, Type, Version]
    C --> H[Communication Parameters<br/>SDO, PDO, SYNC, EMCY]
    
    E --> I[Process Data<br/>0x6000-0x6FFF]
    E --> J[Parameters<br/>0x7000-0x8FFF]
    E --> K[Configuration<br/>0x9000-0x9FFF]
    
    style C fill:#e1f5fe
    style E fill:#c8e6c9
    style D fill:#fff3e0
```

## Object Types and Data Types

### Object Entry Types

| Type | Code | Description | Structure |
|------|------|-------------|-----------|
| **NULL** | 0x00 | Empty object | No data |
| **DOMAIN** | 0x02 | Large data block | Variable length |
| **DEFTYPE** | 0x05 | Data type definition | Type information |
| **DEFSTRUCT** | 0x06 | Structure definition | Complex structure |
| **VAR** | 0x07 | Simple variable | Single value |
| **ARRAY** | 0x08 | Homogeneous array | Same type elements |
| **RECORD** | 0x09 | Heterogeneous record | Different type elements |

### Standard Data Types

```mermaid
graph TD
    A[CANopen Data Types] --> B[Basic Types]
    A --> C[String Types]
    A --> D[Complex Types]
    
    B --> E[BOOLEAN - 1 bit<br/>INTEGER8 - 8 bit<br/>INTEGER16 - 16 bit<br/>INTEGER32 - 32 bit<br/>UNSIGNED8 - 8 bit<br/>UNSIGNED16 - 16 bit<br/>UNSIGNED32 - 32 bit<br/>REAL32 - 32 bit float<br/>REAL64 - 64 bit float]
    
    C --> F[VISIBLE_STRING<br/>OCTET_STRING<br/>UNICODE_STRING]
    
    D --> G[TIME_OF_DAY<br/>TIME_DIFFERENCE<br/>DOMAIN<br/>PDO_MAPPING]
    
    style B fill:#e1f5fe
    style C fill:#c8e6c9
    style D fill:#fff3e0
```

## Communication Objects

### Essential Communication Objects

| Index | Object Name | Description | Access |
|-------|-------------|-------------|--------|
| **0x1000** | Device Type | Device identification | RO |
| **0x1001** | Error Register | Current error status | RO |
| **0x1002** | Manufacturer Status | Vendor-specific status | RO |
| **0x1003** | Pre-defined Error Field | Error history | RW |
| **0x1005** | COB-ID SYNC | SYNC message identifier | RW |
| **0x1006** | Communication Cycle Period | SYNC timing | RW |
| **0x1008** | Manufacturer Device Name | Human-readable name | RO |
| **0x1009** | Manufacturer Hardware Version | Hardware revision | RO |
| **0x100A** | Manufacturer Software Version | Software revision | RO |
| **0x1018** | Identity Object | Complete device identity | RO |

### Identity Object (0x1018) Structure

```mermaid
graph LR
    A[Identity Object<br/>0x1018] --> B[Sub 0: Number of Elements]
    A --> C[Sub 1: Vendor ID]
    A --> D[Sub 2: Product Code]
    A --> E[Sub 3: Revision Number]
    A --> F[Sub 4: Serial Number]
    
    B --> G[0x04]
    C --> H[32-bit Vendor ID]
    D --> I[32-bit Product Code]
    E --> J[32-bit Revision]
    F --> K[32-bit Serial Number]
    
    style A fill:#e1f5fe
```

## SDO Communication Parameters

### SDO Server Parameters (0x1200)

```mermaid
graph TD
    A[SDO Server<br/>0x1200] --> B[Sub 0: Number of Elements]
    A --> C[Sub 1: COB-ID Client→Server]
    A --> D[Sub 2: COB-ID Server→Client]
    A --> E[Sub 3: Node-ID Client]
    
    C --> F[0x600 + Node ID]
    D --> G[0x580 + Node ID]
    E --> H[Master Node ID<br/>or 0xFF for any]
    
    style A fill:#c8e6c9
```

### SDO Client Parameters (0x1280+)

For devices acting as SDO clients (masters):

| Sub-Index | Parameter | Default Value | Description |
|-----------|-----------|---------------|-------------|
| **0** | Number of Elements | 0x03 | Parameter count |
| **1** | COB-ID Server→Client | - | Response CAN ID |
| **2** | COB-ID Client→Server | - | Request CAN ID |
| **3** | Node-ID Server | - | Target device Node ID |

## PDO Communication Parameters

### Receive PDO Parameters (0x1400+)

```mermaid
graph LR
    A[RPDO 1 Parameters<br/>0x1400] --> B[Sub 0: Elements]
    A --> C[Sub 1: COB-ID]
    A --> D[Sub 2: Transmission Type]
    A --> E[Sub 3: Inhibit Time]
    A --> F[Sub 5: Event Timer]
    
    C --> G[0x200 + Node ID<br/>Bit 31: Valid/Invalid]
    D --> H[0-255: Sync types<br/>254-255: Async types]
    E --> I[Minimum time between<br/>transmissions (100μs units)]
    
    style A fill:#fff3e0
```

### Transmit PDO Parameters (0x1800+)

Similar structure to RPDO but for transmitted PDOs:

| Parameter | RPDO Index | TPDO Index | Description |
|-----------|------------|------------|-------------|
| **PDO 1** | 0x1400 | 0x1800 | Highest priority PDO |
| **PDO 2** | 0x1401 | 0x1801 | Second priority PDO |
| **PDO 3** | 0x1402 | 0x1802 | Third priority PDO |
| **PDO 4** | 0x1403 | 0x1803 | Fourth priority PDO |

## PDO Mapping Objects

### PDO Mapping Structure

PDO mapping defines which Object Dictionary entries are packed into PDO messages:

```mermaid
graph TD
    A[PDO Mapping<br/>0x1A00] --> B[Sub 0: Number of Mapped Objects]
    A --> C[Sub 1: 1st Mapped Object]
    A --> D[Sub 2: 2nd Mapped Object]
    A --> E[Sub N: Nth Mapped Object]
    
    C --> F[Bits 31-16: Index<br/>Bits 15-8: Sub-index<br/>Bits 7-0: Length in bits]
    
    style A fill:#e1f5fe
    style F fill:#c8e6c9
```

### Mapping Example

Map three variables into one 8-byte PDO:

| Sub | Index | Sub-Index | Length | Object | Size |
|-----|-------|-----------|--------|--------|------|
| **1** | 0x6040 | 0x00 | 16 bits | Control Word | 2 bytes |
| **2** | 0x6071 | 0x00 | 16 bits | Target Torque | 2 bytes |
| **3** | 0x6077 | 0x00 | 16 bits | Torque Actual | 2 bytes |
| **4** | 0x6061 | 0x00 | 8 bits | Mode of Operation | 1 byte |
| - | - | - | 8 bits | Unused | 1 byte |

## Process Data Objects

### Application Process Data (0x6000-0x6FFF)

Standard process data objects for common industrial applications:

| Index Range | Description | Examples |
|-------------|-------------|----------|
| **0x6000-0x603F** | Digital Inputs | Switch states, sensor inputs |
| **0x6040-0x607F** | Digital Outputs | Actuator control, LED status |
| **0x6080-0x60BF** | Analog Inputs | Sensor readings, measurements |
| **0x60C0-0x60FF** | Analog Outputs | Control signals, setpoints |
| **0x6100-0x613F** | Interrupt Sources | Event triggers, alarms |

### Motor Drive Profile Objects (CiA 402)

Common objects for motor control applications:

| Index | Name | Description | Access |
|-------|------|-------------|--------|
| **0x6040** | Control Word | Motor control commands | RW |
| **0x6041** | Status Word | Motor status feedback | RO |
| **0x6060** | Mode of Operation | Control mode selection | RW |
| **0x6061** | Mode Display | Active control mode | RO |
| **0x607A** | Target Position | Position setpoint | RW |
| **0x6064** | Position Actual | Current position | RO |
| **0x6071** | Target Torque | Torque setpoint | RW |
| **0x6077** | Torque Actual | Current torque | RO |

## SDO Transfer Protocols

### Expedited Transfer (≤4 bytes)

For small data that fits in one SDO message:

```mermaid
sequenceDiagram
    participant C as SDO Client
    participant S as SDO Server
    
    Note over C,S: Write Operation (Download)
    C->>S: Download Request [CCS=1, Index, Sub, Data]
    S->>C: Download Response [SCS=3, Success/Error]
    
    Note over C,S: Read Operation (Upload)  
    C->>S: Upload Request [CCS=2, Index, Sub]
    S->>C: Upload Response [SCS=2, Index, Sub, Data]
```

### Segmented Transfer (>4 bytes)

For large data requiring multiple segments:

```mermaid
sequenceDiagram
    participant C as SDO Client
    participant S as SDO Server
    
    Note over C,S: Segmented Download (Write)
    C->>S: Download Initiate [Size indication]
    S->>C: Download Response [Confirm]
    
    loop For each segment
        C->>S: Download Segment [Data chunk]
        S->>C: Download Response [ACK]
    end
    
    Note over C,S: Segmented Upload (Read)
    C->>S: Upload Initiate [Request]
    S->>C: Upload Response [Size, First segment]
    
    loop For remaining segments
        C->>S: Upload Segment Request [Toggle bit]
        S->>C: Upload Segment Response [Data chunk]
    end
```

## PDO Transmission Modes

### Synchronous PDO Operation

```mermaid
sequenceDiagram
    participant M as SYNC Master
    participant N1 as Node 1
    participant N2 as Node 2
    participant N3 as Node 3
    
    M->>N1: SYNC Message
    M->>N2: SYNC Message
    M->>N3: SYNC Message
    
    Note over N1,N3: SYNC Window - All nodes process inputs
    
    alt Transmission Type 1 (Every SYNC)
        N1->>M: PDO Data
    else Transmission Type 2 (Every 2nd SYNC)
        Note over N2: Skip this SYNC
    else Transmission Type 3 (Every 3rd SYNC)
        N3->>M: PDO Data
    end
```

### Asynchronous PDO Operation

```mermaid
graph TD
    A[Asynchronous PDO Triggers] --> B[Event-driven]
    A --> C[Timer-based]
    A --> D[Application-driven]
    
    B --> E[Input state change<br/>Threshold exceeded<br/>Error condition]
    
    C --> F[Event Timer expired<br/>Periodic transmission<br/>Cyclic updates]
    
    D --> G[Application request<br/>Remote request<br/>Profile-specific]
    
    style B fill:#c8e6c9
    style C fill:#e1f5fe
    style D fill:#fff3e0
```

## Network Management Details

### Node States and Transitions

```mermaid
stateDiagram-v2
    [*] --> PowerOn
    PowerOn --> Initialization
    
    Initialization --> PreOperational : Boot-up complete
    PreOperational --> Operational : NMT Start Node
    PreOperational --> Stopped : NMT Stop Node
    
    Operational --> PreOperational : NMT Pre-operational
    Operational --> Stopped : NMT Stop Node
    
    Stopped --> PreOperational : NMT Pre-operational  
    Stopped --> Operational : NMT Start Node
    
    Initialization --> [*] : Reset Node
    PreOperational --> [*] : Reset Node
    Operational --> [*] : Reset Node
    Stopped --> [*] : Reset Node
    
    note right of PreOperational
        • SDO communication active
        • PDO configuration allowed
        • No process data exchange
        • Network management active
    end note
    
    note right of Operational
        • All communication active
        • Process data exchange
        • Real-time operation
        • Full functionality
    end note
```

### Boot-up Process

```mermaid
sequenceDiagram
    participant N as CANopen Node
    participant M as NMT Master
    participant Net as Network
    
    Note over N: Power-on Reset
    N->>N: Initialize hardware
    N->>N: Load configuration
    N->>N: Initialize communication
    
    N->>Net: Boot-up Message [0x700 + Node ID, 0x00]
    Note over Net: Node announces presence
    
    M->>N: Read Identity Object [SDO]
    N->>M: Identity Response [Vendor, Product, etc.]
    
    M->>N: Configure PDOs [SDO]
    N->>M: Configuration ACK
    
    M->>Net: Start Node [NMT Command]
    Note over N: Enter Operational State
```

## Error Handling and Diagnostics

### Error Register (0x1001)

Single byte register indicating device error status:

| Bit | Error Type | Description |
|-----|------------|-------------|
| **0** | Generic Error | Any unspecified error |
| **1** | Current | Current related error |
| **2** | Voltage | Voltage related error |
| **3** | Temperature | Temperature related error |
| **4** | Communication | Communication error |
| **5** | Device Profile | Profile specific error |
| **6** | Reserved | Must be 0 |
| **7** | Manufacturer | Vendor specific error |

### Pre-defined Error Field (0x1003)

Error history storage:

```mermaid
graph LR
    A[Error Field<br/>0x1003] --> B[Sub 0: Number of Errors]
    A --> C[Sub 1: Most Recent Error]
    A --> D[Sub 2: Previous Error]
    A --> E[Sub N: Oldest Error]
    
    C --> F[32-bit Error Code<br/>Additional Info<br/>Timestamp]
    
    style A fill:#ffcdd2
    style F fill:#fff3e0
```

## Practical Implementation Example

### Simple I/O Device Configuration

Example: 4-channel digital input device

```c
// Object Dictionary entries
typedef struct {
    // Communication Area
    uint32_t device_type;           // 0x1000
    uint8_t  error_register;        // 0x1001
    char     device_name[32];       // 0x1008
    
    // SDO Server parameters
    uint32_t sdo_server_rx_id;      // 0x1200.1
    uint32_t sdo_server_tx_id;      // 0x1200.2
    
    // TPDO1 parameters  
    uint32_t tpdo1_id;              // 0x1800.1
    uint8_t  tpdo1_transmission;    // 0x1800.2
    uint16_t tpdo1_inhibit;         // 0x1800.3
    
    // TPDO1 mapping
    uint8_t  tpdo1_map_count;       // 0x1A00.0
    uint32_t tpdo1_map1;            // 0x1A00.1
    
    // Process Data
    uint8_t  digital_inputs;        // 0x6000
    
} canopen_od_t;

// Initialize Object Dictionary
void init_object_dictionary(uint8_t node_id) {
    od.device_type = 0x00000000;    // Generic I/O device
    strcpy(od.device_name, "4CH Digital Input");
    
    // Configure SDO
    od.sdo_server_rx_id = 0x600 + node_id;
    od.sdo_server_tx_id = 0x580 + node_id;
    
    // Configure TPDO1
    od.tpdo1_id = 0x180 + node_id;
    od.tpdo1_transmission = 254;    // Asynchronous
    od.tpdo1_inhibit = 100;         // 10ms minimum
    
    // Map digital inputs to TPDO1
    od.tpdo1_map_count = 1;
    od.tpdo1_map1 = (0x6000 << 16) | (0x00 << 8) | 8; // 8 bits
}
```

## Learning Objectives Achieved

- ✅ Understand Object Dictionary structure and organization
- ✅ Know communication object parameters and configuration
- ✅ Understand PDO mapping and transmission modes
- ✅ Know SDO transfer protocols and applications
- ✅ Understand error handling and diagnostic mechanisms

## Next Steps

In [Lesson 8: CAN in Robotics Applications](8_can_robotics_applications.md), we'll explore how CAN and CANopen are specifically applied in robotics systems, including sensor networks, actuator control, and distributed control architectures.

## Practical Exercises

1. Design Object Dictionary layout for a 6-DOF robotic arm
2. Configure PDO mapping for simultaneous multi-axis control
3. Implement SDO client to read device configuration
4. Create error handling strategy with EMCY messages
5. Optimize network performance through proper PDO configuration