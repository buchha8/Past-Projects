#!/bin/bash
# Build/deploy script for Innovation Robot server
# Fully user-agnostic, uses separate systemd service file

set -e  # Exit on first error
set -u  # Treat unset variables as errors

# -----------------------------
# 0. Configuration
# -----------------------------
DEV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="/opt/innovation"
VENV_DIR="$DEPLOY_DIR/venv"
DEV_SERVICE="$DEV_DIR/innovation.service"
SYSTEMD_SERVICE="/etc/systemd/system/innovation.service"

# Automatically detect current user and primary group
USER=$(whoami)
GROUP=$(id -gn)

# -----------------------------
# 1. Ensure prerequisites
# -----------------------------
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3-venv python3-pip python3-full rsync

# -----------------------------
# 2. Create deployment directory
# -----------------------------
echo "Creating deployment directory..."
sudo mkdir -p "$DEPLOY_DIR"
sudo chown -R $USER:$GROUP "$DEPLOY_DIR"

# -----------------------------
# 3. Set up virtual environment
# -----------------------------
echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR"

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# -----------------------------
# 4. Install Python dependencies
# -----------------------------
echo "Installing Python dependencies..."
pip install --upgrade pip
if [ -f "$DEV_DIR/requirements.txt" ]; then
    pip install -r "$DEV_DIR/requirements.txt"
else
    echo "ERROR: Requirements file $DEV_DIR/requirements.txt not found!"
    exit 1
fi

# -----------------------------
# 5. Copy server code
# -----------------------------
echo "Copying server code from dev folder..."
rsync -av --exclude='venv' "$DEV_DIR/" "$DEPLOY_DIR/"

# -----------------------------
# 6. Install systemd service
# -----------------------------
if [ ! -f "$DEV_SERVICE" ]; then
    echo "ERROR: Service file $DEV_SERVICE not found!"
    exit 1
fi

echo "Installing systemd service..."
sudo cp "$DEV_SERVICE" "$SYSTEMD_SERVICE"

# Replace USER and GROUP placeholders in the service file
sudo sed -i "s|%iUSER%|$USER|g" "$SYSTEMD_SERVICE"
sudo sed -i "s|%iGROUP%|$GROUP|g" "$SYSTEMD_SERVICE"

# -----------------------------
# 7. Enable and start service
# -----------------------------
echo "Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable innovation.service
sudo systemctl restart innovation.service

echo "Build and deployment complete!"
echo "Check service status with: systemctl status innovation.service"
