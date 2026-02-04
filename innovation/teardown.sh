#!/bin/bash
# Tear-down script for Innovation server
# Stops the service, removes deployment files, and cleans up systemd unit

set -e
set -u

# -----------------------------
# 0. Configuration
# -----------------------------
DEPLOY_DIR="/opt/innovation"
SYSTEMD_SERVICE="/etc/systemd/system/innovation.service"

# Automatically detect current user and group
USER=$(whoami)
GROUP=$(id -gn)

# -----------------------------
# 1. Stop service
# -----------------------------
if systemctl is-active --quiet innovation.service; then
    echo "Stopping innovation.service..."
    sudo systemctl stop innovation.service
else
    echo "innovation.service is not running."
fi

# -----------------------------
# 2. Remove systemd unit
# -----------------------------
if [ -f "$SYSTEMD_SERVICE" ]; then
    echo "Removing systemd service file..."
    sudo rm -f "$SYSTEMD_SERVICE"
    echo "Reloading systemd daemon..."
    sudo systemctl daemon-reload
else
    echo "Systemd service file not found; skipping."
fi

# -----------------------------
# 3. Remove deployment files
# -----------------------------
if [ -d "$DEPLOY_DIR" ]; then
    echo "Deleting deployment directory..."
    sudo rm -rf "$DEPLOY_DIR"
else
    echo "Deployment directory not found; skipping."
fi

# -----------------------------
# 4. Optional: confirmation
# -----------------------------
echo "Tear-down complete."
echo "All files removed, service stopped and disabled."
