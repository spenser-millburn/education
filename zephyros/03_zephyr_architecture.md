# Module 3: Zephyr Architecture and Concepts

## Overview

Zephyr is a small, scalable real-time operating system (RTOS) designed for resource-constrained embedded systems. Understanding its architecture is crucial for effective development.

## Zephyr Architecture Layers

```
┌─────────────────────────┐
│    Application Layer    │  ← Your Code
├─────────────────────────┤
│      Zephyr APIs       │  ← System Calls
├─────────────────────────┤
│    Kernel Services      │  ← Scheduler, IPC, Memory
├─────────────────────────┤
│    Device Drivers       │  ← HAL Abstraction
├─────────────────────────┤
│   Hardware Abstraction  │  ← Architecture Specific
├─────────────────────────┤
│      Hardware          │  ← STM32F446RE
└─────────────────────────┘
```

## Core Concepts

### 1. Kernel Objects

Zephyr provides several kernel objects for application development:

- **Threads**: Units of execution
- **Semaphores**: Counting synchronization primitives
- **Mutexes**: Binary synchronization primitives
- **Message Queues**: Inter-thread communication
- **Timers**: Time-based operations
- **Work Queues**: Deferred work execution

### 2. Memory Management

Zephyr uses several memory allocation strategies:

- **Static Allocation**: Compile-time memory allocation
- **Stack Memory**: Thread-specific stacks
- **Memory Pools**: Runtime memory allocation
- **Memory Slabs**: Fixed-size block allocation

### 3. Device Model

Zephyr's device model provides hardware abstraction:

```c
struct device {
    const char *name;           // Device name
    const void *config;         // Configuration data
    const void *api;            // API structure
    void *data;                 // Runtime data
    const struct device_state *state;
};
```

## Threading Model

### Thread States

```
┌─────────────┐    k_thread_create()    ┌─────────────┐
│   CREATED   │ ────────────────────────→│    READY    │
└─────────────┘                         └─────────────┘
                                                │
                 ┌─────────────┐               │ schedule
                 │  SUSPENDED  │               ▼
                 └─────────────┘        ┌─────────────┐
                        ▲               │   RUNNING   │
                        │               └─────────────┘
                        │                      │
                        │                      │ sleep/wait
                        │                      ▼
                 ┌─────────────┐        ┌─────────────┐
                 │    DEAD     │        │   WAITING   │
                 └─────────────┘        └─────────────┘
```

### Thread Priorities

Zephyr uses priority-based preemptive scheduling:

- **Cooperative Threads**: Priority < 0 (high priority)
- **Preemptive Threads**: Priority ≥ 0 (lower priority)
- **System Threads**: Negative priorities reserved for system

```c
// Thread priority examples
#define HIGH_PRIORITY    -10  // Cooperative thread
#define MEDIUM_PRIORITY   5   // Preemptive thread  
#define LOW_PRIORITY     10   // Lower priority preemptive
```

### Creating Threads

```c
#include <zephyr/kernel.h>

// Thread stack definition
K_THREAD_STACK_DEFINE(my_stack_area, 1024);
struct k_thread my_thread_data;

// Thread function
void my_thread_function(void *arg1, void *arg2, void *arg3)
{
    while (1) {
        printk("Thread running\n");
        k_sleep(K_SECONDS(1));
    }
}

// Create and start thread
int main(void)
{
    k_thread_create(&my_thread_data, my_stack_area,
                    K_THREAD_STACK_SIZEOF(my_stack_area),
                    my_thread_function,
                    NULL, NULL, NULL,
                    5, 0, K_NO_WAIT);
    
    return 0;
}
```

## Device Tree Fundamentals

Device Tree (DT) describes hardware configuration:

### Basic Device Tree Structure

```dts
/dts-v1/;

/ {
    model = "STMicroelectronics STM32F446RE-Nucleo board";
    compatible = "st,stm32f446re-nucleo", "st,stm32f446";

    chosen {
        zephyr,console = &usart2;
        zephyr,shell-uart = &usart2;
        zephyr,sram = &sram0;
        zephyr,flash = &flash0;
    };

    aliases {
        led0 = &green_led;
        sw0 = &user_button;
    };

    leds {
        compatible = "gpio-leds";
        green_led: led_2 {
            gpios = <&gpioa 5 GPIO_ACTIVE_HIGH>;
            label = "User LD2";
        };
    };
};
```

### Device Tree Macros

Zephyr generates C macros from device tree:

```c
// Generated from device tree
#define DT_ALIAS_LED0_GPIOS_CONTROLLER  "gpioa"
#define DT_ALIAS_LED0_GPIOS_PIN         5
#define DT_ALIAS_LED0_GPIOS_FLAGS       GPIO_ACTIVE_HIGH

// Using DT macros in code
#define LED_NODE DT_ALIAS(led0)
static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED_NODE, gpios);
```

## Configuration System (Kconfig)

Kconfig provides compile-time configuration:

### Configuration Types

- **bool**: Boolean options (y/n)
- **int**: Integer values
- **hex**: Hexadecimal values
- **string**: String values

### Configuration Files

- `prj.conf`: Application configuration
- `Kconfig`: Configuration definitions
- `<board>_defconfig`: Board default configuration

Example `prj.conf`:
```ini
# Enable GPIO driver
CONFIG_GPIO=y

# Enable serial console
CONFIG_SERIAL=y
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y

# Enable logging
CONFIG_LOG=y
CONFIG_LOG_DEFAULT_LEVEL=3

# Memory configuration
CONFIG_MAIN_STACK_SIZE=2048
CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=1024
```

## System Calls and APIs

### Kernel APIs

```c
// Thread management
k_thread_create();
k_thread_start();
k_thread_suspend();
k_thread_resume();

// Synchronization
k_sem_init();
k_sem_take();
k_sem_give();
k_mutex_init();
k_mutex_lock();
k_mutex_unlock();

// Timing
k_sleep();
k_timer_init();
k_timer_start();

// Work queues
k_work_init();
k_work_submit();
```

### Device APIs

```c
// GPIO API
gpio_pin_configure();
gpio_pin_get();
gpio_pin_set();
gpio_pin_toggle();

// UART API
uart_configure();
uart_tx();
uart_rx_enable();

// I2C API
i2c_configure();
i2c_write();
i2c_read();
```

## Memory Architecture

### STM32F446RE Memory Layout

```
0x20020000  ┌─────────────────┐  ← End of RAM (128KB)
            │                 │
            │    Free RAM     │
            │                 │
            ├─────────────────┤
            │    Heap         │
            ├─────────────────┤
            │    Stacks       │
            ├─────────────────┤
            │    BSS          │
            ├─────────────────┤
            │    Data         │
0x20000000  └─────────────────┘  ← Start of RAM

0x08080000  ┌─────────────────┐  ← End of Flash (512KB)
            │                 │
            │    Free Flash   │
            │                 │
            ├─────────────────┤
            │    Application  │
            ├─────────────────┤
            │    Zephyr OS    │
            ├─────────────────┤
            │    Vector Table │
0x08000000  └─────────────────┘  ← Start of Flash
```

### Memory Management Example

```c
// Static memory allocation
static char my_buffer[1024];

// Dynamic memory pools
K_MEM_POOL_DEFINE(my_pool, 16, 64, 4, 4);

void allocate_memory(void)
{
    char *ptr;
    
    // Allocate from memory pool
    ptr = k_mem_pool_malloc(&my_pool, 32);
    if (ptr) {
        // Use allocated memory
        strcpy(ptr, "Hello, Zephyr!");
        
        // Free memory
        k_free(ptr);
    }
}
```

## Interrupt Handling

### Interrupt Service Routines (ISR)

```c
#include <zephyr/irq.h>

// ISR function
void my_isr(const struct device *dev, struct gpio_callback *cb,
            uint32_t pins)
{
    printk("Interrupt triggered on pin %d\n", pins);
}

// GPIO callback structure
static struct gpio_callback button_cb_data;

// Configure interrupt
int setup_interrupt(void)
{
    // Configure GPIO pin for interrupt
    gpio_pin_configure_dt(&button, GPIO_INPUT);
    gpio_pin_interrupt_configure_dt(&button, GPIO_INT_EDGE_TO_ACTIVE);
    
    // Initialize callback
    gpio_init_callback(&button_cb_data, my_isr, BIT(button.pin));
    gpio_add_callback(button.port, &button_cb_data);
    
    return 0;
}
```

## Real-Time Capabilities

### Deterministic Behavior

Zephyr provides deterministic real-time behavior:

- **Fixed Priority Scheduling**: Higher priority threads preempt lower priority
- **Priority Inheritance**: Prevents priority inversion
- **Interrupt Latency**: Bounded interrupt response times
- **Context Switch Time**: Predictable thread switching overhead

### Timing Guarantees

```c
// High-precision timing
uint32_t start_time = k_cycle_get_32();
// ... do work ...
uint32_t end_time = k_cycle_get_32();
uint32_t cycles = end_time - start_time;

// Convert to microseconds
uint32_t microseconds = k_cyc_to_us_floor32(cycles);
```

## Power Management

### Power States

- **Active**: CPU and peripherals running
- **Idle**: CPU stopped, peripherals running
- **Standby**: Most peripherals stopped
- **Suspend**: System suspended, minimal power

### Power Management APIs

```c
#include <zephyr/pm/pm.h>

// Request power state
pm_state_set(PM_STATE_SUSPEND_TO_RAM);

// Power management policy
void pm_policy_next_state(uint8_t cpu, int32_t ticks)
{
    if (ticks > 1000) {
        return PM_STATE_SUSPEND_TO_RAM;
    }
    return PM_STATE_ACTIVE;
}
```

## Best Practices

### 1. Resource Management
- Use static allocation when possible
- Size stacks appropriately
- Free allocated resources promptly

### 2. Thread Design
- Keep ISRs short and fast
- Use appropriate thread priorities
- Avoid priority inversion

### 3. Configuration
- Enable only required features
- Optimize for size or speed as needed
- Use device tree for hardware abstraction

### 4. Error Handling
- Check return values
- Use assertions for debugging
- Implement proper error recovery

## Next Steps

Now that you understand Zephyr's architecture, proceed to [Module 4: Project Structure and Build System](04_project_structure.md) to learn about organizing Zephyr projects effectively.