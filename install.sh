#!/bin/bash

# Model-less 6D Pose Estimation - Installation Script
# This script sets up the environment for the pose estimation project

echo "Setting up Model-less 6D Pose Estimation..."
echo "=============================================="

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "Python $python_version detected (>= $required_version required)"
else
    echo "Python 3.8+ is required. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "pip3 detected"

# Create virtual environment (optional)
read -p "Do you want to create a virtual environment? (y/n): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment created and activated"
fi

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully"
else
    echo "Failed to install dependencies. Please check your internet connection and try again."
    exit 1
fi

# Generate ChArUco board
echo "Generating ChArUco calibration board..."
python3 charuco_generate.py

if [ $? -eq 0 ]; then
    echo "ChArUco board generated as 'charuco_board.png'"
    echo "Please print this file for camera calibration"
else
    echo "Failed to generate ChArUco board"
    exit 1
fi

# Check for RealSense camera
echo "Checking for Intel RealSense camera..."
if python3 -c "import pyrealsense2 as rs; print('RealSense SDK found')" 2>/dev/null; then
    echo "RealSense SDK is installed"
    
    # Try to detect RealSense camera
    if python3 -c "
import pyrealsense2 as rs
try:
    ctx = rs.context()
    devices = ctx.query_devices()
    if len(devices) > 0:
        print(f'Found {len(devices)} RealSense device(s)')
        for device in devices:
            print(f'  - {device.get_info(rs.camera_info.name)}')
    else:
        print('No RealSense devices found')
except Exception as e:
    print('Error detecting RealSense devices:', e)
" 2>/dev/null; then
        echo "RealSense camera detection completed"
    else
        echo "Could not detect RealSense cameras (this is normal if no camera is connected)"
    fi
else
    echo "RealSense SDK not found. Please install it manually:"
    echo "   Visit: https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python"
fi

echo ""
echo "Installation completed successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Print the generated 'charuco_board.png' file"
echo "2. Run camera calibration: python3 calibration_charuco.py"
echo "3. Run pose estimation: python3 6D_pose_color.py"
echo ""
echo "For more information, see README.md"
echo ""
echo "Happy pose estimating!" 