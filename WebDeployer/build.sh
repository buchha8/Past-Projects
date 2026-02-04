#!/bin/bash
# Build/deploy script for deployed server
# Fully user-agnostic, uses separate systemd service file

set -e  # Exit on first error
set -u  # Treat unset variables as errors

# -----------------------------
# 0. Load project configuration
# -----------------------------
CONFIG_FILE="$(dirname "${BASH_SOURCE[0]}")/project.conf"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file $CONFIG_FILE not found!"
    exit 1
fi
source "$CONFIG_FILE"

DEV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_SERVICE="$DEV_DIR/service.template"

# Automatically detect current user and primary group
USER=$(whoami)
GROUP=$(id -gn)

# -----------------------------
# 1. Ensure TLS certificates exist
# -----------------------------
echo "Ensuring TLS certificates exist..."
sudo mkdir -p "$CERT_DIR"
sudo chown -R $USER:$GROUP "$CERT_DIR"
sudo chmod 750 "$CERT_DIR"

if [ ! -f "$KEY_FILE" ] || [ ! -f "$CERT_FILE" ]; then
    echo "Generating self-signed TLS certificate..."
    openssl req -x509 -newkey rsa:4096 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -days 365 \
        -nodes \
        -subj "/CN=$PROJECT_NAME"
    chmod 640 "$KEY_FILE" "$CERT_FILE"
else
    echo "TLS certificates already exist; skipping generation."
fi

# -----------------------------
# 2. Ensure prerequisites
# -----------------------------
echo "Installing system dependencies..."
sudo apt install -y python3-venv python3-pip python3-full rsync

# -----------------------------
# 3. Create deployment directory
# -----------------------------
echo "Creating deployment directory..."
sudo mkdir -p "$DEPLOY_DIR"
sudo chown -R $USER:$GROUP "$DEPLOY_DIR"

# -----------------------------
# 4. Set up virtual environment
# -----------------------------
echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR"

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# -----------------------------
# 5. Install Python dependencies
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
# 6. Copy server code
# -----------------------------
echo "Copying server code from dev folder..."
rsync -av --exclude='venv' "$DEV_DIR/" "$DEPLOY_DIR/"

# -----------------------------
# 7. Install systemd service
# -----------------------------
if [ ! -f "$DEV_SERVICE" ]; then
    echo "ERROR: Service template $DEV_SERVICE not found!"
    exit 1
fi

echo "Installing systemd service..."
sudo sed \
    -e "s|%USER%|$USER|g" \
    -e "s|%GROUP%|$GROUP|g" \
    -e "s|%PROJECT_NAME%|$PROJECT_NAME|g" \
    -e "s|%DEPLOY_DIR%|$DEPLOY_DIR|g" \
    -e "s|%VENV_DIR%|$VENV_DIR|g" \
    -e "s|%KEY_FILE%|$KEY_FILE|g" \
    -e "s|%CERT_FILE%|$CERT_FILE|g" \
    "$DEV_SERVICE" | sudo tee "$SYSTEMD_SERVICE" > /dev/null

sudo sed "s|%PROJECT_NAME%|$PROJECT_NAME|g" "$DEPLOY_DIR/dashboard.html" \
    | sudo tee "$DEPLOY_DIR/dashboard.html" > /dev/null

# -----------------------------
# 8. Enable and start service
# -----------------------------
echo "Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable "$PROJECT_NAME.service"
sudo systemctl restart "$PROJECT_NAME.service"

echo "Build and deployment complete!"
echo "Check service status with: systemctl status $PROJECT_NAME.service"
