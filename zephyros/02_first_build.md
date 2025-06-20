# Module 2: First Build and Flash

## Understanding the Build Process

Zephyr uses the West meta-tool for building and flashing applications. This module covers the build system and creating your first custom application.

## Build System Overview

- **West**: Meta-tool for managing Zephyr projects
- **CMake**: Build system generator
- **Ninja**: Fast build system (default)
- **Device Tree**: Hardware description language
- **Kconfig**: Configuration system

## Build Process Flow

1. **Configure**: Kconfig processes configuration files
2. **Generate**: CMake generates build files
3. **Compile**: Compiler builds source code
4. **Link**: Linker creates final binary
5. **Post-process**: Generate additional formats (hex, bin)

## Building Sample Applications

### Hello World Sample

```bash
# Navigate to Zephyr directory
cd ~/zephyr-dev/zephyrproject/zephyr

# Build hello_world sample
west build -p auto -b nucleo_f446re samples/hello_world

# Flash to board
west flash

# View serial output
west attach
```

### Blinky Sample

```bash
# Build blinky sample
west build -p auto -b nucleo_f446re samples/basic/blinky

# Flash and run
west flash
```

## Understanding Build Output

The build process creates several important files:

```
build/
├── zephyr/
│   ├── zephyr.elf      # ELF executable
│   ├── zephyr.hex      # Intel HEX format
│   ├── zephyr.bin      # Raw binary
│   ├── zephyr.map      # Memory map
│   └── zephyr.config   # Final configuration
└── build.ninja         # Ninja build file
```

## Creating Your First Custom Application

### Step 1: Create Project Structure

```bash
# Create project directory
mkdir ~/zephyr-dev/my_first_app
cd ~/zephyr-dev/my_first_app

# Create source directory
mkdir src
```

### Step 2: Create Main Source File

Create `src/main.c`:

```c
#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/printk.h>

/* LED configuration */
#define LED_NODE DT_ALIAS(led0)
static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED_NODE, gpios);

/* Main application thread */
int main(void)
{
    int ret;
    bool led_state = true;

    printk("Starting STM32 Nucleo-F446RE Application\n");

    /* Check if LED device is ready */
    if (!gpio_is_ready_dt(&led)) {
        printk("Error: LED device not ready\n");
        return -1;
    }

    /* Configure LED pin as output */
    ret = gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);
    if (ret < 0) {
        printk("Error: Failed to configure LED pin\n");
        return -1;
    }

    printk("LED configured successfully\n");

    /* Main loop */
    while (1) {
        /* Toggle LED */
        ret = gpio_pin_toggle_dt(&led);
        if (ret < 0) {
            printk("Error: Failed to toggle LED\n");
            return -1;
        }

        led_state = !led_state;
        printk("LED is %s\n", led_state ? "ON" : "OFF");

        /* Wait 1 second */
        k_sleep(K_SECONDS(1));
    }

    return 0;
}
```

### Step 3: Create CMakeLists.txt

Create `CMakeLists.txt`:

```cmake
# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)

# Find Zephyr package
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})

# Set project name
project(my_first_app)

# Add source files
target_sources(app PRIVATE src/main.c)
```

### Step 4: Create Configuration File

Create `prj.conf`:

```ini
# Enable GPIO driver
CONFIG_GPIO=y

# Enable console and logging
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y
CONFIG_SERIAL=y

# Enable printk
CONFIG_PRINTK=y

# Optional: Enable logging framework
CONFIG_LOG=y
CONFIG_LOG_DEFAULT_LEVEL=3
```

### Step 5: Build and Flash

```bash
# Build the application
west build -p auto -b nucleo_f446re

# Flash to board
west flash

# Connect to serial console
west attach
```

## Build Commands Reference

### Basic Build Commands

```bash
# Clean build (rebuild everything)
west build -p auto -b <board> <source_dir>

# Incremental build
west build

# Clean build directory
west build -t clean

# Build specific target
west build -t <target>
```

### Flash and Debug Commands

```bash
# Flash application
west flash

# Flash with specific runner
west flash --runner openocd

# Debug application
west debug

# Attach to serial console
west attach
```

### Configuration Commands

```bash
# Open menuconfig
west build -t menuconfig

# Open guiconfig
west build -t guiconfig

# List all configuration options
west build -t hardenconfig
```

## Understanding Device Tree

The STM32 Nucleo-F446RE board configuration is defined in device tree files:

```
boards/arm/nucleo_f446re/
├── nucleo_f446re.dts          # Main board definition
├── nucleo_f446re.yaml         # Board metadata
├── nucleo_f446re_defconfig    # Default Kconfig
└── board.cmake                # Board CMake config
```

### Key Device Tree Nodes

```dts
/ {
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

    buttons {
        compatible = "gpio-keys";
        user_button: button {
            label = "User";
            gpios = <&gpioc 13 GPIO_ACTIVE_LOW>;
        };
    };
};
```

## Common Build Issues and Solutions

### Issue: Board Not Found
```bash
# List available boards
west boards | grep nucleo

# Verify board name
west build -b nucleo_f446re --help
```

### Issue: SDK Not Found
```bash
# Check environment variables
echo $ZEPHYR_SDK_INSTALL_DIR
echo $ZEPHYR_TOOLCHAIN_VARIANT

# Re-export Zephyr
west zephyr-export
```

### Issue: Flash Failure
```bash
# Check board connection
lsusb | grep STM

# Try different flash runner
west flash --runner openocd
west flash --runner stm32cubeprogrammer
```

### Issue: Missing Dependencies
```bash
# Install missing packages
sudo dnf install -y cmake ninja-build gperf

# Update Python requirements
pip install -r ~/zephyr-dev/zephyrproject/zephyr/scripts/requirements.txt
```

## Build Optimization

### Faster Builds

```bash
# Use ccache for faster compilation
export USE_CCACHE=1

# Parallel builds (use number of CPU cores)
west build -- -j$(nproc)
```

### Smaller Binaries

Add to `prj.conf`:
```ini
# Optimize for size
CONFIG_SIZE_OPTIMIZATIONS=y

# Disable debug info
CONFIG_DEBUG_INFO=n

# Disable assertions
CONFIG_ASSERT=n
```

## Next Steps

Now that you understand the build process, proceed to [Module 3: Zephyr Architecture and Concepts](03_zephyr_architecture.md) to learn about Zephyr's internal architecture and design principles.