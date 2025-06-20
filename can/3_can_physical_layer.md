# Lesson 3: CAN Physical Layer and Network Topology

## Physical Layer Overview

The CAN physical layer defines the electrical characteristics, signal levels, and timing parameters that enable reliable communication across the network. Understanding these aspects is crucial for designing robust CAN systems.

## CAN Bus Electrical Properties

### Signal Levels

CAN uses differential signaling with two wires: CAN High (CAN_H) and CAN Low (CAN_L).

| State | CAN_H Voltage | CAN_L Voltage | Differential Voltage | Bit Value |
|-------|---------------|---------------|---------------------|-----------|
| **Dominant** | 3.5V | 1.5V | 2.0V | 0 |
| **Recessive** | 2.5V | 2.5V | 0.0V | 1 |

```mermaid
graph TD
    A[CAN Signal States] --> B[Dominant State]
    A --> C[Recessive State]
    
    B --> D[CAN_H: 3.5V<br/>CAN_L: 1.5V<br/>Diff: 2.0V<br/>Bit: 0]
    
    C --> E[CAN_H: 2.5V<br/>CAN_L: 2.5V<br/>Diff: 0.0V<br/>Bit: 1]
    
    style B fill:#ffcdd2
    style C fill:#c8e6c9
```

### Why Differential Signaling?

```mermaid
graph LR
    A[Benefits] --> B[Noise Immunity]
    A --> C[Long Distance]
    A --> D[Common Mode Rejection]
    A --> E[EMI Reduction]
    
    B --> F[External interference<br/>affects both lines equally]
    C --> G[Lower signal<br/>degradation over distance]
    D --> H[Receiver detects<br/>difference, not absolute levels]
    E --> I[Balanced transmission<br/>reduces electromagnetic emission]
```

## CAN Transceiver Architecture

```mermaid
graph TD
    A[Microcontroller] --> B[CAN Controller]
    B --> C[CAN Transceiver]
    C --> D[CAN_H]
    C --> E[CAN_L]
    
    F[Bus Termination<br/>120Ω] --> D
    F --> E
    
    G[Other Nodes] --> D
    G --> E
    
    H[Bus Termination<br/>120Ω] --> D
    H --> E
    
    style C fill:#e1f5fe
    style F fill:#ffcdd2
    style H fill:#ffcdd2
```

## Common CAN Transceiver Types

| Transceiver | Standard | Speed | Features |
|-------------|----------|-------|----------|
| **MCP2551** | ISO 11898 | 1 Mbps | Basic, low-cost |
| **TJA1050** | ISO 11898 | 1 Mbps | Automotive grade |
| **SN65HVD230** | ISO 11898 | 1 Mbps | 3.3V operation |
| **MCP2562** | ISO 11898 | 1 Mbps | Fault protection |
| **TJA1042** | ISO 11898 | 5 Mbps | CAN-FD capable |

## Network Topology

### Linear Bus Topology

CAN networks use a **linear bus topology** with proper termination:

```mermaid
graph LR
    A[Terminator<br/>120Ω] --> B[Main Bus]
    B --> C[Node 1]
    B --> D[Node 2]
    B --> E[Node 3]
    B --> F[Node N]
    B --> G[Terminator<br/>120Ω]
    
    C --> H[Stub ≤ 0.3m]
    D --> I[Stub ≤ 0.3m]
    E --> J[Stub ≤ 0.3m]
    F --> K[Stub ≤ 0.3m]
    
    style A fill:#ffcdd2
    style G fill:#ffcdd2
    style B fill:#e3f2fd
```

### Stub Length Limitations

| Bus Speed | Maximum Stub Length |
|-----------|-------------------|
| 1 Mbps | 0.3 m |
| 500 kbps | 0.6 m |
| 250 kbps | 1.2 m |
| 125 kbps | 2.4 m |

## Bus Termination

### Why Termination is Critical

```mermaid
graph TD
    A[Without Termination] --> B[Signal Reflections]
    A --> C[Impedance Mismatch]
    A --> D[Communication Errors]
    
    E[With Proper Termination] --> F[Clean Signal Transitions]
    E --> G[Matched Impedance]
    E --> H[Reliable Communication]
    
    style A fill:#ffcdd2
    style E fill:#c8e6c9
```

### Termination Methods

#### Standard Termination (120Ω)
```mermaid
graph LR
    A[CAN_H] --> B[120Ω Resistor]
    B --> C[CAN_L]
    
    style B fill:#ffcdd2
```

#### Split Termination (Automotive)
```mermaid
graph LR
    A[CAN_H] --> B[60Ω]
    B --> C[Node]
    C --> D[60Ω]
    D --> E[CAN_L]
    
    C --> F[4.7nF]
    F --> G[Ground]
    
    style B fill:#e1f5fe
    style D fill:#e1f5fe
    style F fill:#fff3e0
```

## Bit Timing and Synchronization

### Bit Time Structure

Each bit time is divided into segments:

```mermaid
gantt
    title CAN Bit Time Segments
    dateFormat X
    axisFormat %s
    
    section Bit Segments
    Sync Segment     :sync, 0, 1
    Prop Segment     :prop, after sync, 2
    Phase Seg 1      :ph1, after prop, 3
    Phase Seg 2      :ph2, after ph1, 2
    
    section Sample Point
    Sample Point     :milestone, sample, 6, 0
```

### Timing Parameters

| Parameter | Description | Range |
|-----------|-------------|-------|
| **Sync Segment** | Synchronization | 1 TQ |
| **Prop Segment** | Propagation delay compensation | 1-8 TQ |
| **Phase Seg 1** | Buffer before sample point | 1-8 TQ |
| **Phase Seg 2** | Buffer after sample point | 1-8 TQ |
| **Sample Point** | Bit value sampling location | 60-90% |

### Time Quantum (TQ) Calculation

```
TQ = 2 × (BRP + 1) / f_osc

Where:
- BRP = Baud Rate Prescaler
- f_osc = Oscillator frequency
```

## Speed vs Distance Relationship

```mermaid
graph LR
    A[Bus Speed] --> B[Maximum Distance]
    
    B --> C[1 Mbps → 25m]
    B --> D[500 kbps → 100m]
    B --> E[250 kbps → 250m]
    B --> F[125 kbps → 500m]
    B --> G[50 kbps → 1000m]
    B --> H[10 kbps → 5000m]
    
    style C fill:#ffcdd2
    style D fill:#fff3e0
    style E fill:#e8f5e8
    style F fill:#e1f5fe
    style G fill:#f3e5f5
    style H fill:#fce4ec
```

## Cable Specifications

### Recommended Cable Types

| Application | Cable Type | Impedance | Characteristics |
|-------------|------------|-----------|-----------------|
| **Automotive** | Twisted pair | 120Ω ± 5% | Shielded, flame retardant |
| **Industrial** | DeviceNet cable | 120Ω ± 5% | Rugged, EMI resistant |
| **Marine** | Marine grade | 120Ω ± 5% | Water resistant, tinned copper |
| **Aerospace** | Aerospace grade | 120Ω ± 5% | Lightweight, high temperature |

### Cable Construction

```mermaid
graph TD
    A[CAN Cable] --> B[Twisted Pair]
    A --> C[Shield]
    A --> D[Outer Jacket]
    
    B --> E[CAN_H Wire]
    B --> F[CAN_L Wire]
    B --> G[Twist Rate:<br/>20-50 twists/meter]
    
    C --> H[Braided Shield<br/>or Foil Wrap]
    D --> I[PVC, PUR, or<br/>Halogen-free]
    
    style B fill:#e1f5fe
    style C fill:#fff3e0
    style D fill:#e8f5e8
```

## Grounding and Shielding

### Proper Grounding Strategy

```mermaid
graph TD
    A[CAN Network Grounding] --> B[Single Point Ground]
    A --> C[Shield Connection]
    A --> D[Ground Loops Prevention]
    
    B --> E[Connect all node grounds<br/>to common reference]
    C --> F[Shield grounded at<br/>one end only]
    D --> G[Avoid multiple<br/>ground paths]
    
    style B fill:#c8e6c9
    style C fill:#e1f5fe
    style D fill:#ffcdd2
```

## Environmental Considerations

### Operating Conditions

| Parameter | Automotive | Industrial | Military |
|-----------|------------|------------|----------|
| **Temperature** | -40°C to +125°C | -40°C to +85°C | -55°C to +125°C |
| **Humidity** | 95% RH | 85% RH | 95% RH |
| **Vibration** | 20G | 10G | 30G |
| **EMI Immunity** | High | Medium | Very High |

## Common Physical Layer Issues

### Signal Quality Problems

```mermaid
graph TD
    A[Physical Layer Issues] --> B[Improper Termination]
    A --> C[Ground Loops]
    A --> D[EMI Interference]
    A --> E[Cable Issues]
    
    B --> F[Missing terminators<br/>Wrong value terminators<br/>Multiple terminators]
    
    C --> G[Multiple ground paths<br/>Ground potential differences]
    
    D --> H[Switching power supplies<br/>Motors and relays<br/>Radio transmissions]
    
    E --> I[Incorrect impedance<br/>Damaged cables<br/>Poor connections]
    
    style B fill:#ffcdd2
    style C fill:#fff3e0
    style D fill:#ffe0b2
    style E fill:#f8bbd9
```

## Network Design Guidelines

### Best Practices Checklist

| Guideline | Requirement | Importance |
|-----------|-------------|------------|
| **Topology** | Linear bus only | Critical |
| **Termination** | Exactly 2 × 120Ω resistors | Critical |
| **Stub Length** | ≤ 0.3m at 1 Mbps | High |
| **Cable Impedance** | 120Ω ± 5% | High |
| **Grounding** | Single point reference | High |
| **Shielding** | Ground at one end only | Medium |

## Voltage Supply Considerations

### Power Supply Requirements

```mermaid
graph TD
    A[CAN Node Power] --> B[Microcontroller]
    A --> C[CAN Transceiver]
    A --> D[Decoupling]
    
    B --> E[3.3V or 5V<br/>Low noise<br/>Stable regulation]
    
    C --> F[5V typical<br/>Low dropout<br/>Current capability]
    
    D --> G[100nF ceramic<br/>10μF electrolytic<br/>Close to IC]
    
    style B fill:#e1f5fe
    style C fill:#e8f5e8
    style D fill:#fff3e0
```

## Testing Physical Layer

### Measurement Points

| Test | Measurement | Expected Value |
|------|-------------|----------------|
| **Bus Resistance** | CAN_H to CAN_L | 60Ω (with nodes) |
| **Termination** | Each end | 120Ω |
| **Dominant Voltage** | CAN_H - CAN_L | 2.0V ± 0.5V |
| **Recessive Voltage** | CAN_H - CAN_L | 0.0V ± 0.5V |
| **Rise/Fall Time** | 10%-90% | < 250ns |

## Learning Objectives Achieved

- ✅ Understand CAN electrical characteristics and differential signaling
- ✅ Know proper network topology and termination requirements
- ✅ Understand bit timing and synchronization mechanisms
- ✅ Recognize speed vs distance limitations
- ✅ Know cable specifications and grounding best practices
- ✅ Identify common physical layer issues and solutions

## Next Steps

In [Lesson 4: CAN Arbitration and Error Handling](4_can_arbitration_error_handling.md), we'll explore how CAN manages multiple simultaneous transmissions and maintains network reliability through sophisticated error detection and handling mechanisms.

## Practical Exercises

1. Calculate the maximum network length for a 250 kbps CAN network
2. Determine the total bus resistance for a network with 8 nodes
3. Design termination for a high-EMI environment
4. Calculate bit timing parameters for 500 kbps with 16 MHz crystal
5. Troubleshoot a network with intermittent communication errors