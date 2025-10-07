#!/bin/bash

# This script tunes a Linux server for high-concurrency networking.
# It is idempotent and can be run safely multiple times.

echo "--- Starting Server Performance Tuning ---"

LIMITS_FILE="/etc/security/limits.conf"
SYSCTL_FILE="/etc/sysctl.conf"
SYSTEMD_SYSTEM_FILE="/etc/systemd/system.conf"
SYSTEMD_USER_FILE="/etc/systemd/user.conf"

# --- 1. Set File Descriptor Limits in limits.conf ---
echo "Updating file descriptor limits in $LIMITS_FILE..."
if grep -q "^\* soft nofile" "$LIMITS_FILE"; then
    sed -i 's/^\* soft nofile.*/\* soft nofile 65536/' "$LIMITS_FILE"
else
    echo '* soft nofile 65536' >> "$LIMITS_FILE"
fi

if grep -q "^\* hard nofile" "$LIMITS_FILE"; then
    sed -i 's/^\* hard nofile.*/\* hard nofile 65536/' "$LIMITS_FILE"
else
    echo '* hard nofile 65536' >> "$LIMITS_FILE"
fi

# --- 2. Set System-Wide Max Files in sysctl.conf ---
echo "Updating max files in $SYSCTL_FILE..."
if grep -q "^fs.file-max" "$SYSCTL_FILE"; then
    sed -i 's/^fs.file-max.*/fs.file-max = 2097152/' "$SYSCTL_FILE"
else
    echo 'fs.file-max = 2097152' >> "$SYSCTL_FILE"
fi

# --- 2.5. Tune Network Settings for High Concurrency ---
echo "Updating network settings in $SYSCTL_FILE..."
# Set somaxconn for large backlog
if grep -q "^net.core.somaxconn" "$SYSCTL_FILE"; then
    sed -i 's/^net.core.somaxconn.*/net.core.somaxconn = 65535/' "$SYSCTL_FILE"
else
    echo 'net.core.somaxconn = 65535' >> "$SYSCTL_FILE"
fi
# Set ephemeral port range for high outbound connections
if grep -q "^net.ipv4.ip_local_port_range" "$SYSCTL_FILE"; then
    sed -i 's/^net.ipv4.ip_local_port_range.*/net.ipv4.ip_local_port_range = 1024 65535/' "$SYSCTL_FILE"
else
    echo 'net.ipv4.ip_local_port_range = 1024 65535' >> "$SYSCTL_FILE"
fi
# Enable TCP TIME_WAIT reuse
if grep -q "^net.ipv4.tcp_tw_reuse" "$SYSCTL_FILE"; then
    sed -i 's/^net.ipv4.tcp_tw_reuse.*/net.ipv4.tcp_tw_reuse = 1/' "$SYSCTL_FILE"
else
    echo 'net.ipv4.tcp_tw_reuse = 1' >> "$SYSCTL_FILE"
fi

# --- 3. Set Default Systemd Process Limit ---
echo "Updating DefaultLimitNOFILE in systemd configs..."
sed -i 's/^#\?DefaultLimitNOFILE=.*/DefaultLimitNOFILE=65536/' "$SYSTEMD_SYSTEM_FILE"
sed -i 's/^#\?DefaultLimitNOFILE=.*/DefaultLimitNOFILE=65536/' "$SYSTEMD_USER_FILE"


# --- 4. Apply sysctl changes immediately ---
echo "Applying sysctl changes..."
sysctl -p

echo ""
echo "--- Tuning Complete ---"
echo "A REBOOT is required for all changes to take full effect."
echo ""
echo "If the script did not update files properly, manually:"
echo "  - Edit /etc/security/limits.conf: add '* soft nofile 65536' and '* hard nofile 65536'"
echo "  - Edit /etc/sysctl.conf: fs.file-max=2097152, somaxconn=65535, ip_local_port_range=1024 65535, tcp_tw_reuse=1; then sysctl -p"
echo "  - Edit /etc/systemd/system.conf and user.conf: set DefaultLimitNOFILE=65536; then systemctl daemon-reload"
echo "Verify with 'ulimit -n' and 'sysctl fs.file-max net.ipv4.ip_local_port_range'"