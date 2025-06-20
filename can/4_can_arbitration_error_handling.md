# Lesson 4: CAN Arbitration and Error Handling

## CAN Arbitration Overview

CAN arbitration is the mechanism that allows multiple nodes to compete for bus access simultaneously without causing collisions. This **non-destructive arbitration** process ensures that the highest priority message is transmitted while lower priority messages automatically back off.

## How Arbitration Works

### Wired-AND Logic

CAN bus implements **wired-AND logic** where:
- **Dominant (0)** beats **Recessive (1)**
- Any node transmitting dominant forces the bus to dominant state
- Multiple nodes can read the bus while transmitting

```mermaid
graph TD
    A[CAN Arbitration Process] --> B[Multiple Nodes Start Transmission]
    B --> C[Compare Identifier Bits]
    C --> D{Transmitted bit matches bus?}
    D -->|Yes| E[Continue Transmission]
    D -->|No| F[Back Off - Lost Arbitration]
    E --> G{More ID bits?}
    G -->|Yes| C
    G -->|No| H[Winner Continues with Frame]
    F --> I[Retry in Next Opportunity]
    
    style H fill:#c8e6c9
    style F fill:#ffcdd2
```

### Arbitration Example

Consider three nodes attempting to transmit simultaneously:

| Bit Position | Node A (ID: 0x123) | Node B (ID: 0x124) | Node C (ID: 0x120) | Bus State |
|--------------|---------------------|---------------------|---------------------|-----------|
| 10 | 0 | 0 | 0 | 0 (dominant) |
| 9 | 0 | 0 | 0 | 0 (dominant) |
| 8 | 0 | 0 | 0 | 0 (dominant) |
| 7 | 1 | 1 | 1 | 1 (recessive) |
| 6 | 0 | 0 | 0 | 0 (dominant) |
| 5 | 0 | 0 | 0 | 0 (dominant) |
| 4 | 0 | 0 | 0 | 0 (dominant) |
| 3 | 0 | 0 | 0 | 0 (dominant) |
| 2 | 1 | 1 | **0** | **0** (C wins) |
| 1 | **Backs off** | **Backs off** | 0 | 0 |
| 0 | - | - | 0 | 0 |

```mermaid
sequenceDiagram
    participant A as Node A (0x123)
    participant B as Node B (0x124) 
    participant C as Node C (0x120)
    participant Bus as CAN Bus
    
    A->>Bus: Starts transmitting 0x123
    B->>Bus: Starts transmitting 0x124
    C->>Bus: Starts transmitting 0x120
    
    Note over A,Bus: Bits 10-3: All nodes transmit same values
    
    A->>Bus: Bit 2: Sends 1 (recessive)
    B->>Bus: Bit 2: Sends 1 (recessive)
    C->>Bus: Bit 2: Sends 0 (dominant)
    Bus-->>A: Reads 0 - Lost arbitration!
    Bus-->>B: Reads 0 - Lost arbitration!
    Bus-->>C: Reads 0 - Continue
    
    Note over A: Backs off, will retry later
    Note over B: Backs off, will retry later
    Note over C: Wins arbitration, completes transmission
```

## Priority Determination

### Standard Frame Priority

For standard 11-bit identifiers, priority is determined by:

```mermaid
graph LR
    A[Highest Priority] --> B[Lower Numerical Value]
    B --> C[0x000 has highest priority]
    C --> D[0x7FF has lowest priority]
    
    E[ID Bits] --> F[MSB compared first]
    F --> G[Bit-by-bit comparison]
    G --> H[First dominant bit wins]
    
    style A fill:#c8e6c9
    style D fill:#ffcdd2
```

### Extended Frame Priority

Extended frames have lower priority than standard frames with the same base ID:

| Frame Type | Base ID | Extended ID | Overall Priority |
|------------|---------|-------------|------------------|
| Standard | 0x123 | - | **Higher** |
| Extended | 0x123 | 0x45678 | Lower |

## Error Detection Mechanisms

CAN implements multiple layers of error detection to ensure data integrity:

```mermaid
graph TD
    A[CAN Error Detection] --> B[Frame-Level Errors]
    A --> C[Bit-Level Errors]
    A --> D[Message-Level Errors]
    
    B --> E[Form Error]
    B --> F[CRC Error]
    B --> G[ACK Error]
    
    C --> H[Bit Error]
    C --> I[Stuff Error]
    
    D --> J[Message Timeout]
    D --> K[Sequence Error]
    
    style B fill:#e1f5fe
    style C fill:#e8f5e8
    style D fill:#fff3e0
```

## Error Types in Detail

### 1. Bit Error

Occurs when a transmitted bit differs from the received bit.

```mermaid
sequenceDiagram
    participant T as Transmitter
    participant B as Bus
    participant R as Receiver
    
    T->>B: Transmits: 1 (recessive)
    Note over B: Noise causes bit flip
    B->>R: Receives: 0 (dominant)
    R->>B: Detects bit error!
    B->>T: Error frame transmitted
```

### 2. Stuff Error

Violation of bit stuffing rule (more than 5 consecutive identical bits).

```
Correct:   1 1 1 1 1 0 0 0 1 1 1 1 1 0
           └─────┘   ↑         └─────┘   ↑
           5 bits   stuff      5 bits   stuff
           
Error:     1 1 1 1 1 1 0 1 1 1 1 1 1 1
           └───────┘           └───────┘
           6 bits!             7 bits!
```

### 3. CRC Error

Cyclic Redundancy Check detects data corruption:

```mermaid
graph LR
    A[Transmitted Data] --> B[CRC Calculation]
    B --> C[Append CRC]
    C --> D[Send Frame]
    
    E[Received Frame] --> F[Extract Data]
    F --> G[Recalculate CRC]
    G --> H{CRC Match?}
    H -->|Yes| I[Accept Frame]
    H -->|No| J[CRC Error!]
    
    style I fill:#c8e6c9
    style J fill:#ffcdd2
```

### 4. Form Error

Invalid frame format (e.g., dominant bit in EOF field):

| Field | Expected | Error Condition |
|-------|----------|-----------------|
| **EOF** | 7 recessive bits | Any dominant bit |
| **IFS** | 3 recessive bits | Dominant in first 3 bits |
| **Reserved bits** | Must be dominant | Recessive bit |

### 5. ACK Error

No acknowledgment received from other nodes:

```mermaid
sequenceDiagram
    participant T as Transmitter
    participant N as Network Nodes
    participant B as Bus
    
    T->>B: Transmits complete frame
    T->>B: ACK slot: recessive (expecting ACK)
    
    alt Normal Operation
        N->>B: Drives ACK slot dominant
        B-->>T: ACK received - success
    else ACK Error
        N-->>B: No response (all nodes busy/failed)
        B-->>T: ACK slot remains recessive
        T->>B: Transmits error frame
    end
```

## Error Handling States

CAN controllers implement error handling through state machines:

```mermaid
stateDiagram-v2
    [*] --> ErrorActive
    
    ErrorActive --> ErrorPassive : TEC or REC > 127
    ErrorPassive --> ErrorActive : TEC and REC < 128
    ErrorPassive --> BusOff : TEC > 255
    BusOff --> ErrorActive : 128 × 11 recessive bits
    
    note right of ErrorActive
        Normal operation
        Transmits active error frames
        TEC, REC < 128
    end note
    
    note right of ErrorPassive
        Limited operation
        Transmits passive error frames
        127 < TEC or REC < 256
    end note
    
    note right of BusOff
        No bus activity allowed
        Must be reset
        TEC > 255
    end note
```

## Error Counters

CAN maintains two error counters per node:

| Counter | Description | Increment Rules | Decrement Rules |
|---------|-------------|-----------------|-----------------|
| **TEC** | Transmit Error Counter | +8 per transmit error | -1 per successful transmission |
| **REC** | Receive Error Counter | +1 per receive error | -1 per successful reception |

### Error Counter Rules

```mermaid
graph TD
    A[Error Occurs] --> B{Error Type}
    B -->|Transmit Error| C[TEC += 8]
    B -->|Receive Error| D[REC += 1]
    B -->|Stuff Error by Transmitter| E[TEC += 8]
    B -->|Stuff Error by Receiver| F[REC += 1]
    
    G[Successful Transmission] --> H[TEC -= 1]
    I[Successful Reception] --> J[REC -= 1]
    
    style C fill:#ffcdd2
    style D fill:#ffcdd2
    style H fill:#c8e6c9
    style J fill:#c8e6c9
```

## Error Frames

### Active Error Frame

Transmitted by error-active nodes:

```
┌─────────────┬─────────────┐
│ Error Flag  │   Error     │
│  (6 bits)   │ Delimiter   │
│ dominant    │  (8 bits)   │
│             │ recessive   │
└─────────────┴─────────────┘
```

### Passive Error Frame

Transmitted by error-passive nodes:

```
┌─────────────┬─────────────┐
│ Error Flag  │   Error     │
│  (6 bits)   │ Delimiter   │
│ recessive   │  (8 bits)   │
│             │ recessive   │
└─────────────┴─────────────┘
```

## Error Recovery Mechanisms

### Automatic Retransmission

```mermaid
graph TD
    A[Transmission Attempt] --> B{Error Detected?}
    B -->|No| C[Successful Transmission]
    B -->|Yes| D[Increment Error Counter]
    D --> E{Node State OK?}
    E -->|Yes| F[Schedule Retransmission]
    E -->|No| G[Enter Error State]
    F --> H[Wait for Bus Idle]
    H --> I[Retry Transmission]
    I --> A
    
    style C fill:#c8e6c9
    style G fill:#ffcdd2
```

### Bus Recovery Procedure

For bus-off recovery:

1. **Enter Bus-Off State**: TEC > 255
2. **Monitor Bus**: Wait for 128 × 11 consecutive recessive bits
3. **Reset Counters**: TEC = 0, REC = 0
4. **Return to Error-Active**: Resume normal operation

## Network-Level Error Handling

### Error Confinement

```mermaid
graph TD
    A[Faulty Node Detection] --> B[Error Counter Increases]
    B --> C{Error Threshold?}
    C -->|TEC/REC > 127| D[Error Passive State]
    C -->|TEC > 255| E[Bus Off State]
    D --> F[Reduced Network Impact]
    E --> G[Node Isolation]
    
    style F fill:#fff3e0
    style G fill:#ffcdd2
```

### Babbling Node Protection

Prevention of nodes continuously transmitting errors:

| Protection Method | Implementation |
|-------------------|----------------|
| **Error Counters** | Automatic state transitions |
| **Watchdog Timers** | External monitoring |
| **Bus Monitoring** | Network-level supervision |
| **Protocol Validation** | Frame format checking |

## Error Statistics and Monitoring

### Key Metrics to Monitor

```mermaid
graph LR
    A[Error Monitoring] --> B[Error Rate]
    A --> C[Error Types]
    A --> D[Node Status]
    A --> E[Bus Utilization]
    
    B --> F[Errors per second<br/>Errors per message]
    C --> G[CRC, ACK, Form<br/>Bit, Stuff errors]
    D --> H[Error states<br/>Counter values]
    E --> I[Message load<br/>Bus idle time]
```

### Diagnostic Information

| Metric | Normal Range | Warning Threshold | Critical Threshold |
|--------|--------------|-------------------|-------------------|
| **Error Rate** | < 0.1% | 0.1% - 1% | > 1% |
| **TEC/REC** | < 96 | 96 - 127 | > 127 |
| **Bus Utilization** | < 80% | 80% - 95% | > 95% |
| **Response Time** | < 10ms | 10ms - 50ms | > 50ms |

## Common Error Scenarios

### Scenario 1: Intermittent Connection

```mermaid
sequenceDiagram
    participant N1 as Node 1
    participant N2 as Node 2
    participant N3 as Node 3
    
    N1->>N2: Normal communication
    N1->>N3: Normal communication
    
    Note over N2: Loose connection
    
    N1->>N2: Message sent
    N2-->>N1: No ACK (connection issue)
    N1->>N1: ACK Error, increment TEC
    
    N1->>N2: Retry transmission
    N2->>N1: ACK received (connection restored)
    N1->>N1: Success, decrement TEC
```

### Scenario 2: EMI Interference

```mermaid
graph TD
    A[EMI Source] --> B[Signal Distortion]
    B --> C[Bit Errors]
    C --> D[Multiple Nodes Detect Errors]
    D --> E[Error Frames Transmitted]
    E --> F[Bus Recovery]
    F --> G{EMI Continues?}
    G -->|Yes| H[Repeated Errors]
    G -->|No| I[Normal Operation]
    
    style A fill:#ffcdd2
    style H fill:#ffcdd2
    style I fill:#c8e6c9
```

## Learning Objectives Achieved

- ✅ Understand non-destructive arbitration mechanism
- ✅ Know different error types and detection methods
- ✅ Understand error states and counter mechanisms
- ✅ Recognize error recovery procedures
- ✅ Know how to monitor and diagnose network errors

## Next Steps

In [Lesson 5: CAN-FD (Flexible Data-Rate) Protocol](5_can_fd_protocol.md), we'll explore the enhanced CAN-FD protocol that provides higher data rates and larger payload capacity while maintaining backward compatibility.

## Practical Exercises

1. Determine the arbitration winner between IDs: 0x100, 0x101, 0x0FF
2. Calculate error counter values after 10 transmit errors and 5 successful transmissions
3. Design error handling strategy for a safety-critical robotics application
4. Analyze error patterns to identify potential network issues
5. Implement error monitoring and logging for CAN network diagnostics