#!/bin/bash
# High-performance server tuning script

echo "--- Starting Server Performance Tuning ---"

SYSCTL_FILE="/etc/sysctl.conf"
NGINX_CONF="/etc/nginx/sites-available/forevercode.online"
DOMAIN="forevercode.online"

# --- 1. Tune Kernel for High Concurrency ---
echo "Updating kernel network settings..."
# Set somaxconn for a large backlog queue
if grep -q "^net.core.somaxconn" "$SYSCTL_FILE"; then
    sed -i 's/^net.core.somaxconn.*/net.core.somaxconn = 65535/' "$SYSCTL_FILE"
else
    echo 'net.core.somaxconn = 65535' >> "$SYSCTL_FILE"
fi
# Apply settings immediately
sysctl -p

# --- 2. Create High-Performance Nginx Config ---
echo "Creating Nginx config for $DOMAIN..."
cat > "$NGINX_CONF" <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    # Use ssl, http2, and the large backlog queue we configured
    listen 443 ssl http2 backlog=65535;
    server_name $DOMAIN www.$DOMAIN;

    # !!! IMPORTANT !!!
    # You must replace these paths with the actual paths provided by certbot
    # The script will fail without valid certificate files.
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