#!/bin/bash
# Setup script for exposing Regen Network API to ChatGPT
# Run with: sudo bash setup-chatgpt-endpoint.sh

set -e

NGINX_CONF="/etc/nginx/sites-enabled/regen-digests.conf"
API_PORT=8008
API_PATH="/regen-api"
DOMAIN="regen.gaiaai.xyz"

echo "=============================================="
echo "Regen Network API - ChatGPT Endpoint Setup"
echo "=============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run with sudo"
    exit 1
fi

# Check if nginx config exists
if [ ! -f "$NGINX_CONF" ]; then
    echo "Error: Nginx config not found at $NGINX_CONF"
    exit 1
fi

# Check if location block already exists
if grep -q "location /regen-api" "$NGINX_CONF"; then
    echo "Location block for /regen-api already exists in nginx config"
    echo "Skipping nginx configuration..."
else
    echo "Adding /regen-api location block to nginx config..."

    # Create the location block
    LOCATION_BLOCK='
    # Regen Network API - ChatGPT Actions endpoint
    location /regen-api/ {
        proxy_pass http://127.0.0.1:8008/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120;
        proxy_connect_timeout 60;
    }
'

    # Backup the config
    cp "$NGINX_CONF" "${NGINX_CONF}.bak.$(date +%Y%m%d_%H%M%S)"
    echo "Created backup of nginx config"

    # Insert the location block before the last closing brace of the 443 server block
    # We'll insert it before the final closing brace
    sed -i '/^}$/i\
    # Regen Network API - ChatGPT Actions endpoint\
    location /regen-api/ {\
        proxy_pass http://127.0.0.1:8008/;\
        proxy_http_version 1.1;\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
        proxy_set_header X-Forwarded-Proto $scheme;\
        proxy_read_timeout 120;\
        proxy_connect_timeout 60;\
    }' "$NGINX_CONF"

    echo "Added location block to nginx config"
fi

# Test nginx configuration
echo ""
echo "Testing nginx configuration..."
if nginx -t; then
    echo "Nginx config test passed"
else
    echo "Error: Nginx config test failed!"
    echo "Restoring backup..."
    LATEST_BACKUP=$(ls -t ${NGINX_CONF}.bak.* 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        cp "$LATEST_BACKUP" "$NGINX_CONF"
        echo "Backup restored"
    fi
    exit 1
fi

# Reload nginx
echo ""
echo "Reloading nginx..."
systemctl reload nginx
echo "Nginx reloaded"

# Restart PM2 service (as the original user, not root)
echo ""
echo "Restarting PM2 service..."
SUDO_USER_HOME=$(getent passwd $SUDO_USER | cut -d: -f6)
sudo -u $SUDO_USER bash -c "pm2 restart regen-network-api"
echo "PM2 service restarted"

# Wait for service to start
echo ""
echo "Waiting for API to start..."
sleep 3

# Test local endpoint
echo ""
echo "Testing local endpoint..."
LOCAL_RESPONSE=$(curl -s http://localhost:$API_PORT/ 2>/dev/null || echo "FAILED")
if echo "$LOCAL_RESPONSE" | grep -q "Regen Network API"; then
    echo "Local endpoint OK: http://localhost:$API_PORT/"
else
    echo "Warning: Local endpoint not responding"
fi

# Test public endpoint
echo ""
echo "Testing public endpoint..."
PUBLIC_RESPONSE=$(curl -s https://$DOMAIN$API_PATH/ 2>/dev/null || echo "FAILED")
if echo "$PUBLIC_RESPONSE" | grep -q "Regen Network API"; then
    echo "Public endpoint OK: https://$DOMAIN$API_PATH/"
else
    echo "Warning: Public endpoint not responding (may need a moment)"
fi

# Summary
echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "API Endpoints:"
echo "  Local:    http://localhost:$API_PORT/"
echo "  Public:   https://$DOMAIN$API_PATH/"
echo "  Docs:     https://$DOMAIN$API_PATH/docs"
echo "  Schema:   https://$DOMAIN$API_PATH/openapi.json"
echo ""
echo "ChatGPT Setup:"
echo "  1. Go to ChatGPT -> Create a GPT -> Configure"
echo "  2. Click 'Create new action'"
echo "  3. Click 'Import from URL' and enter:"
echo "     https://$DOMAIN$API_PATH/openapi.json"
echo "  4. Set Authentication to 'None'"
echo "  5. Save and test your GPT!"
echo ""
echo "=============================================="
