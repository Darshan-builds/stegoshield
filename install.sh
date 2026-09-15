#!/usr/bin/env bash
set -e

echo "=================================================="
echo "🛡️  StegoShield — Linux Automated Installer"
echo "=================================================="

# Detect package manager
if command -v apt-get &>/dev/null; then
    echo "[1/4] Installing system dependencies via apt..."
    sudo apt-get update -y
    sudo apt-get install -y python3-venv python3-full libgl1 libegl1 libxkbcommon-x11-0 \
        libxcb-cursor0 libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
        libxcb-randr0 libxcb-render-util0 libxcb-shape0
elif command -v dnf &>/dev/null; then
    echo "[1/4] Installing system dependencies via dnf..."
    sudo dnf install -y python3-virtualenv mesa-libGL libxkbcommon-x11 xcb-util-cursor
elif command -v pacman &>/dev/null; then
    echo "[1/4] Installing system dependencies via pacman..."
    sudo pacman -Sy --noconfirm python libglvnd libxkbcommon-x11 xcb-util-cursor
fi

# Setup Virtual Environment
echo "[2/4] Setting up Python virtual environment (venv)..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install requirements with timeout and retry protection
echo "[3/4] Installing Python packages..."
pip install --upgrade pip --default-timeout=1000
pip install --default-timeout=1000 --retries 10 -r requirements.txt

# Launch StegoShield
echo "[4/4] Launching StegoShield..."
echo "=================================================="
python app.py
