# ChatGPT REST API Deployment Guide

## Quick Start

```bash
# Install dependencies
uv sync

# Run the API
python chatgpt_rest_api_v2.py
```

The API runs on `http://0.0.0.0:8006` by default.

## Endpoints

- **API Root**: `http://localhost:8006/`
- **Swagger Docs**: `http://localhost:8006/docs`
- **OpenAPI Schema**: `http://localhost:8006/openapi.json`

## Production Deployment

### 1. Environment Variables (Optional)

Edit the top of `chatgpt_rest_api_v2.py` to add env var support if needed:
```python
import os
PORT = int(os.getenv("PORT", 8006))
HOST = os.getenv("HOST", "0.0.0.0")
```

### 2. Systemd Service

Create `/etc/systemd/system/regen-api.service`:
```ini
[Unit]
Description=Regen Network ChatGPT REST API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/regen-python-mcp
ExecStart=/usr/bin/python3 chatgpt_rest_api_v2.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable regen-api
sudo systemctl start regen-api
```

### 3. Nginx Reverse Proxy (with SSL)

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8006;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. CORS Configuration

Current CORS allows ChatGPT domains. Edit `chatgpt_rest_api_v2.py` line ~102 if you need to restrict further:
```python
allow_origins=["https://chat.openai.com", "https://chatgpt.com"],
```

## Testing

```bash
# Run automated tests (API must be running)
python test_chatgpt_api_v2.py

# Quick endpoint test
curl http://localhost:8006/
```

## API Overview

25 endpoints consolidating 45 Regen Network queries:
- **Ecocredits**: Credit types, classes, projects, batches
- **Marketplace**: Sell orders, allowed denoms
- **Baskets**: List, get, fees, balances
- **Bank**: Accounts, balances, supply, metadata
- **Distribution**: Params, pool, validator/delegator rewards
- **Governance**: Params, proposals, votes, tally
- **Analytics**: Portfolio analysis, market trends, methodology comparison

## ChatGPT GPT Setup

1. Create new GPT at chat.openai.com
2. Go to Configure → Actions → Create new action
3. Import from URL: `https://your-domain.com/openapi.json`
4. Save and test
