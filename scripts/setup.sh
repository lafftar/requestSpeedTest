#!/bin/bash
set -e # Exit immediately if a command fails

echo "--- [Step 1/3] Installing prerequisites... ---"
sudo apt-get update
# Install git, the default python3 venv package, and ca-certificates all at once
sudo apt-get install -y git python3-venv ca-certificates tmux systemd-resolved
# `sudo nano /etc/systemd/resolved.conf` -> `DNS=1.1.1.1 8.8.8.8`
sudo systemctl enable systemd-resolved && sudo systemctl start systemd-resolved

echo ""
echo "--- [Step 2/3] Cloning repository and setting up Python environment... ---"
# Remove existing directory if it's there to ensure a clean start
rm -rf requestSpeedTest
git clone https://github.com/lafftar/requestSpeedTest.git
cd requestSpeedTest

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "Python environment created and dependencies installed."

echo ""
echo "--- [Step 3/3] Applying server performance tuning... ---"
# Assumes the script is in a subdirectory called 'scripts'
bash scripts/tune_server.sh

echo ""
echo "--- SETUP COMPLETE ---"
echo "Please reboot the server now by running: sudo reboot"