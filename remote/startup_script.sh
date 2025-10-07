#!/bin/bash
# High-performance server tuning script
# Only run this after certbot has run!

echo "--- Starting Server Performance Tuning ---"

SYSCTL_FILE="/etc/sysctl.conf"
NGINX_CONF="/etc/nginx/sites-available/forevercode.online"
NGINX_MAIN_CONF="/etc/nginx/nginx.conf"
DOMAIN="forevercode.online"

# --- 1. Tune Kernel for High Concurrency ---
echo "Updating kernel network settings..."
# Ensure the sysctl conf file exists before trying to read it
touch "$SYSCTL_FILE"
# Set somaxconn for a large backlog queue
if grep -q "^net.core.somaxconn" "$SYSCTL_FILE"; then
    sed -i 's/^net.core.somaxconn.*/net.core.somaxconn = 65535/' "$SYSCTL_FILE"
else
    echo 'net.core.somaxconn = 65535' >> "$SYSCTL_FILE"
fi
# Apply settings immediately
sysctl -p

# --- 1.2. Increase Open File Limits ---
echo "Increasing open file limits..."
LIMITS_FILE="/etc/security/limits.conf"
# Add nofile limits for all users
if ! grep -q "* soft nofile" "$LIMITS_FILE"; then
    echo '* soft nofile 65536' >> "$LIMITS_FILE"
fi
if ! grep -q "* hard nofile" "$LIMITS_FILE"; then
    echo '* hard nofile 65536' >> "$LIMITS_FILE"
fi
# For systemd services, edit nginx service to set LimitNOFILE
NGINX_SERVICE="/lib/systemd/system/nginx.service"
if [ -f "$NGINX_SERVICE" ]; then
    if ! grep -q "LimitNOFILE" "$NGINX_SERVICE"; then
        sed -i '/\[Service\]/a\LimitNOFILE=65536' "$NGINX_SERVICE"
        systemctl daemon-reload
    fi
fi

# --- 1.5. Tune Nginx for High Concurrency ---
echo "Updating Nginx worker settings..."
# Ensure the nginx conf file exists before trying to read it
touch "$NGINX_MAIN_CONF"
# Set worker_processes to auto for multi-core utilization
sed -i 's/.*worker_processes.*/worker_processes auto;/' "$NGINX_MAIN_CONF"
# Set worker_connections for high concurrency
sed -i 's/.*worker_connections.*/    worker_connections 65535;/' "$NGINX_MAIN_CONF"

# --- 2. Create High-Performance Nginx Config ---
echo "Creating Nginx config for $DOMAIN..."
cat > "$NGINX_CONF" <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 200 \$remote_addr;
}

server {
    listen 443 ssl backlog=65535;
    http2 on; # Updated, modern syntax for enabling HTTP/2
    http2_max_concurrent_streams 1000;

    server_name $DOMAIN www.$DOMAIN;

    # !!! IMPORTANT !!!
    # You must have already run certbot for these files to exist.
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    location / {
        default_type text/plain;
        return 200 \$remote_addr;
    }
}
EOF

# --- 3. Enable Site and Restart Nginx ---
echo "Enabling site and restarting Nginx..."
if [ ! -L /etc/nginx/sites-enabled/$DOMAIN ]; then
    ln -s "$NGINX_CONF" /etc/nginx/sites-enabled/
fi
if [ -L /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

# Test config and restart
nginx -t && systemctl restart nginx

echo "--- Tuning Complete. Server is configured for HTTP/2 and high throughput. ---"
echo ""
echo "If the script did not update files properly, manually:"
echo "  - Edit /etc/sysctl.conf: net.core.somaxconn=65535; then sysctl -p"
echo "  - Edit /etc/nginx/nginx.conf: set worker_processes auto; and worker_connections 65535;"
echo "  - Edit /etc/security/limits.conf: add '* soft nofile 65536' and '* hard nofile 65536'"
echo "  - Edit /lib/systemd/system/nginx.service: add LimitNOFILE=65536 in [Service], then systemctl daemon-reload"
echo "Then run 'sudo nginx -t && sudo systemctl restart nginx'"
echo "Verify with 'sysctl net.core.somaxconn' and 'grep worker /etc/nginx/nginx.conf'"