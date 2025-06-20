# Zephyr RTOS Course - STM32 Nucleo-F446RE

## Course Overview

This comprehensive course teaches Zephyr RTOS development using the STM32 Nucleo-F446RE development board. The course is designed for developers working with VSCode on Fedora 41.

## Target Hardware

- **Board**: STM32 Nucleo-F446RE
- **MCU**: STM32F446RET6
- **Architecture**: ARM Cortex-M4F
- **Flash**: 512 KB
- **RAM**: 128 KB
- **Clock**: up to 180 MHz

## Development Environment

- **OS**: Fedora 41
- **IDE**: Visual Studio Code
- **Build System**: West (Zephyr's meta-tool)
- **Toolchain**: Zephyr SDK

## Course Structure

### Module 1: Setup and Environment
1. [Development Environment Setup](01_environment_setup.md)
2. [First Build and Flash](02_first_build.md)

### Module 2: Zephyr Fundamentals  
3. [Zephyr Architecture and Concepts](03_zephyr_architecture.md)
4. [Project Structure and Build System](04_project_structure.md)

### Module 3: Basic Applications
5. [Hello World Application](05_hello_world.md)
6. [GPIO and LED Control](06_gpio_leds.md)
7. [Button Input and Interrupts](07_buttons_interrupts.md)

### Module 4: Real-Time Features
8. [Threading and Scheduling](08_threading_scheduling.md)
9. [Synchronization Primitives](09_synchronization.md)
10. [Timers and Timing](10_timers_timing.md)

### Module 5: Device Drivers and Hardware
11. [Device Tree and Hardware Abstraction](11_devicetree_hardware.md)
12. [UART Communication](12_uart_communication.md)
13. [I2C Communication](13_i2c_communication.md)
14. [SPI Communication](14_spi_communication.md)

### Module 6: Advanced Topics
15. [ADC and Sensors](15_adc_sensors.md)
16. [PWM and Motor Control](16_pwm_motors.md)
17. [Power Management](17_power_management.md)

### Module 7: Development and Debugging
18. [Debugging Techniques](18_debugging.md)
19. [Testing and Validation](19_testing.md)
20. [Performance Optimization](20_optimization.md)

## Prerequisites

- Basic C programming knowledge
- Understanding of embedded systems concepts
- Familiarity with microcontroller peripherals
- Linux command line basics

## Learning Objectives

By the end of this course, you will:
- Set up a complete Zephyr development environment
- Build and deploy Zephyr applications to STM32 hardware
- Understand Zephyr's real-time operating system concepts
- Implement multi-threaded embedded applications
- Use hardware peripherals through Zephyr's device drivers
- Debug and optimize Zephyr applications
- Apply best practices for embedded software development

## Getting Started

Begin with [Module 1: Development Environment Setup](01_environment_setup.md) to configure your development environment.