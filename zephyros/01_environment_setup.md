# Module 1: Development Environment Setup

## Prerequisites

- Fedora 41 Linux system
- STM32 Nucleo-F446RE board
- USB cable (typically USB-A to Mini-USB)
- Internet connection for package downloads

## Step 1: Install System Dependencies

Update your Fedora system and install required packages:

```bash
# Update system packages
sudo dnf update -y

# Install development tools
sudo dnf groupinstall -y "Development Tools" "C Development Tools and Libraries"

# Install Python and pip
sudo dnf install -y python3 python3-pip python3-venv

# Install Git and other utilities
sudo dnf install -y git wget curl cmake ninja-build gperf ccache dfu-util dtc

# Install additional dependencies for Zephyr
sudo dnf install -y libusb-devel libudev-devel
```

## Step 2: Install Visual Studio Code

```bash
# Add Microsoft GPG key and repository
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'

# Install VS Code
sudo dnf install -y code
```

## Step 3: Set Up Python Virtual Environment

```bash
# Create a dedicated directory for Zephyr development
mkdir -p ~/zephyr-dev
cd ~/zephyr-dev

# Create Python virtual environment
python3 -m venv zephyr-env

# Activate the virtual environment
source zephyr-env/bin/activate

# Upgrade pip and install West
pip install --upgrade pip
pip install west
```

## Step 4: Install Zephyr SDK

```bash
# Download Zephyr SDK (version 0.16.5-1 as of writing)
cd ~/zephyr-dev
wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.16.5/zephyr-sdk-0.16.5_linux-x86_64.tar.xz

# Extract the SDK
tar xf zephyr-sdk-0.16.5_linux-x86_64.tar.xz

# Run the SDK setup script
cd zephyr-sdk-0.16.5
./setup.sh

# Add udev rules for USB devices (required for flashing)
sudo cp ~/zephyr-dev/zephyr-sdk-0.16.5/sysroots/x86_64-pokysdk-linux/usr/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d/
sudo udevadm control --reload
```

## Step 5: Initialize Zephyr Workspace

```bash
# Navigate to your development directory
cd ~/zephyr-dev

# Initialize West workspace
west init zephyrproject
cd zephyrproject

# Update Zephyr and all modules
west update

# Export Zephyr CMake package (run this from zephyr directory)
west zephyr-export

# Install additional Python dependencies
pip install -r zephyr/scripts/requirements.txt
```

## Step 6: Configure Environment Variables

Add these lines to your `~/.bashrc` file:

```bash
# Add to ~/.bashrc
echo 'export ZEPHYR_TOOLCHAIN_VARIANT=zephyr' >> ~/.bashrc
echo 'export ZEPHYR_SDK_INSTALL_DIR=~/zephyr-dev/zephyr-sdk-0.16.5' >> ~/.bashrc
echo 'source ~/zephyr-dev/zephyr-env/bin/activate' >> ~/.bashrc

# Reload bash configuration
source ~/.bashrc
```

## Step 7: Install VS Code Extensions

Open VS Code and install these essential extensions:

1. **C/C++** (Microsoft)
2. **C/C++ Extension Pack** (Microsoft) 
3. **CMake Tools** (Microsoft)
4. **Python** (Microsoft)
5. **DeviceTree** (plorefice)
6. **Zephyr IDE** (Nordic Semiconductor)

Install via command line:
```bash
code --install-extension ms-vscode.cpptools
code --install-extension ms-vscode.cpptools-extension-pack
code --install-extension ms-vscode.cmake-tools
code --install-extension ms-python.python
code --install-extension plorefice.devicetree
code --install-extension nordic-semiconductor.nrf-devicetree
```

## Step 8: Test Hardware Connection

Connect your STM32 Nucleo-F446RE board to your computer via USB.

```bash
# Check if the board is detected
lsusb | grep STM

# Check for ST-Link interface
ls /dev/ttyACM*
```

You should see output similar to:
```
Bus 001 Device 005: ID 0483:374b STMicroelectronics ST-LINK/V2.1
/dev/ttyACM0
```

## Step 9: Build and Flash Test Application

```bash
# Navigate to Zephyr samples directory
cd ~/zephyr-dev/zephyrproject/zephyr

# Build hello_world sample for nucleo_f446re
west build -p auto -b nucleo_f446re samples/hello_world

# Flash the application to the board
west flash

# Connect to serial console (optional)
picocom /dev/ttyACM0 -b 115200
```

If successful, you should see "Hello World!" output in the console.

## Step 10: Configure VS Code Workspace

Create a VS Code workspace configuration:

```bash
# Create workspace directory
mkdir ~/zephyr-dev/workspace
cd ~/zephyr-dev/workspace

# Create VS Code settings
mkdir .vscode
```

Create `.vscode/settings.json`:
```json
{
    "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools",
    "cmake.sourceDirectory": "${workspaceFolder}",
    "cmake.buildDirectory": "${workspaceFolder}/build",
    "python.defaultInterpreterPath": "~/zephyr-dev/zephyr-env/bin/python",
    "python.terminal.activateEnvironment": true
}
```

## Troubleshooting

### Permission Issues
If you encounter permission issues with USB devices:
```bash
# Add your user to dialout group
sudo usermod -a -G dialout $USER
# Log out and log back in
```

### SDK Not Found
If West can't find the SDK:
```bash
# Verify environment variables
echo $ZEPHYR_SDK_INSTALL_DIR
echo $ZEPHYR_TOOLCHAIN_VARIANT

# Re-run SDK setup if needed
cd ~/zephyr-dev/zephyr-sdk-0.16.5

./setup.sh
```

### Build Errors
For CMake or build errors:
```bash
# Clean build directory
west build -t clean
# Or rebuild from scratch
west build -p auto -b nucleo_f446re samples/hello_world
```

## Next Steps

Once your environment is set up successfully, proceed to [Module 2: First Build and Flash](02_first_build.md) to learn about the build process and create your first custom application.