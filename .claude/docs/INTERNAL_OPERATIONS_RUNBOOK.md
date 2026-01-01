# Internal Operations Runbook

This runbook documents production infrastructure, service management, and operational procedures for the Regen Network API system. **This document is for internal use only — NOT exposed to GPT.**

## Production Environment

### Server Access

```bash
# Primary production server
ssh darren@202.61.196.119

# Project locations
/opt/projects/regen-python-mcp    # REST API + OpenAPI specs
/opt/projects/koi-processor       # KOI search + knowledge graph
/opt/projects/GAIA                # Telegram bot + content dashboard
```

### Public Endpoints

| Service | URL | Port |
|---------|-----|------|
| Unified API (GPT) | https://regen.gaiaai.xyz | 443 (nginx) |
| Regen Ledger API | https://regen.gaiaai.xyz/regen-api/* | 8008 (internal) |
| KOI Knowledge API | https://regen.gaiaai.xyz/api/koi/* | 3030 (internal) |
| Graph Visualization | https://regen.gaiaai.xyz/graph | 3030 |

## Service Management

### Service Types by Component

| Service | Manager | Port | Config File |
|---------|---------|------|-------------|
| regen-network-api | **pm2** | 8008 | `regen-python-mcp/ecosystem.config.js` |
| hybrid-rag-api (KOI) | **pm2** | 3030 | `koi-processor/ecosystem.hybrid.config.js` |
| content-dashboard | **systemd** | 8400 | `/etc/systemd/system/content-dashboard.service` |
| koi-bge | **systemd** | 8090 | `/etc/systemd/system/koi-bge.service` |
| koi-bridge | **systemd** | 8100 | `/etc/systemd/system/koi-bridge.service` |
| nginx | **systemd** | 80/443 | `/etc/nginx/sites-enabled/` |

**IMPORTANT**: The content-dashboard runs on port 8400 via systemd. Do NOT create a duplicate pm2 process on this port.

### pm2 Commands

```bash
# View all pm2 processes
pm2 list

# Restart services
pm2 restart regen-network-api
pm2 restart hybrid-rag-api

# View logs
pm2 logs regen-network-api
pm2 logs hybrid-rag-api --lines 100

# Monitor
pm2 monit
```

### systemd Commands

```bash
# Content dashboard
sudo systemctl status content-dashboard
sudo systemctl restart content-dashboard
sudo journalctl -u content-dashboard -f

# KOI infrastructure
sudo systemctl status koi-bge
sudo systemctl status koi-bridge
sudo systemctl restart koi-bge koi-bridge

# View recent logs
sudo journalctl -u content-dashboard --since "1 hour ago"
```

## Assessment Runner

The assessment runner validates API coverage and scenario testing.

### Location

```bash
cd /Users/darrenzal/projects/RegenAI/scripts/assessment
# OR on server:
cd /opt/projects/RegenAI/scripts/assessment
```

### Commands

```bash
# Install dependencies (first time)
npm install

# Run coverage tests (API endpoint validation)
npm run coverage

# Run scenario tests (user journey simulation)
npm run scenario

# Run metrics collection
npm run metrics

# Run full assessment suite
npm run full
```

### Report Locations

Reports are saved to timestamped directories:

```
scripts/assessment/results/
├── coverage_2025-12-31T18-08-08-256Z/
│   ├── responses.json        # Raw API responses
│   ├── summary.json          # Coverage metrics
│   └── errors.json           # Failed requests
├── scenario_2025-12-31T05-54-11-317Z/
│   ├── responses.json
│   └── evaluation.json       # Scenario pass/fail
└── metrics_*/
    └── metrics.json          # Performance data
```

### Quick Validation

```bash
# Test single endpoint
curl -s https://regen.gaiaai.xyz/regen-api/summary | jq .name

# Test KOI search
curl -s https://regen.gaiaai.xyz/api/koi/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is regenerative agriculture?", "limit": 3}' | jq .total_results

# Test weekly digest
curl -s https://regen.gaiaai.xyz/api/koi/weekly-digest | jq .period
```

## Database Access

### PostgreSQL (KOI Data)

```bash
# On production server
cd /opt/projects/koi-processor
set -a && source .env && set +a

# Connect to database
psql $POSTGRES_URL

# Quick stats
psql $POSTGRES_URL -c "SELECT COUNT(*) FROM koi_documents;"
psql $POSTGRES_URL -c "SELECT COUNT(*) FROM entity_registry;"
```

### Docker Services

```bash
# PostgreSQL container
docker ps | grep postgres
# Usually: gaia-postgres-1 on port 5433

# Fuseki (SPARQL/graph)
docker ps | grep fuseki
# Usually: fuseki-koi on port 3030
```

## Nginx Configuration

### Relevant Config Files

```bash
# Main site config
/etc/nginx/sites-enabled/regen.gaiaai.xyz

# Proxy locations (within site config):
# /regen-api/* -> http://127.0.0.1:8008
# /api/koi/*   -> http://127.0.0.1:3030
# /graph       -> http://127.0.0.1:3030
```

### Reload After Changes

```bash
sudo nginx -t                    # Test config
sudo systemctl reload nginx      # Apply changes
```

## Monitoring & Health Checks

### Quick Health Check

```bash
# API health
curl -s https://regen.gaiaai.xyz/regen-api/ | jq .version

# KOI health (internal only, not GPT-exposed)
curl -s http://localhost:3030/api/koi/health | jq .status

# Check all services
pm2 list && sudo systemctl status koi-bge koi-bridge content-dashboard --no-pager
```

### Log Locations

| Service | Log Path |
|---------|----------|
| regen-network-api | `/opt/projects/regen-python-mcp/logs/pm2-*.log` |
| hybrid-rag-api | `/opt/projects/koi-processor/logs/pm2-*.log` |
| koi-bge/bridge | `journalctl -u koi-bge` / `journalctl -u koi-bridge` |
| nginx | `/var/log/nginx/access.log`, `/var/log/nginx/error.log` |

## Deployment Procedures

### Deploy OpenAPI Changes

```bash
cd /opt/projects/regen-python-mcp

# Pull latest
git pull

# Validate schema
python scripts/validate_openapi_gpt.py --strict

# Restart API (picks up new openapi-gpt.json)
pm2 restart regen-network-api
```

### Deploy KOI Changes

```bash
cd /opt/projects/koi-processor

# Pull latest
git pull

# Install deps if needed
bun install

# Restart
pm2 restart hybrid-rag-api
```

## Troubleshooting

### API Returns 502/503

1. Check if service is running: `pm2 list`
2. Check logs: `pm2 logs regen-network-api --lines 50`
3. Restart if needed: `pm2 restart regen-network-api`
4. Check nginx: `sudo nginx -t && sudo systemctl status nginx`

### KOI Search Returns Empty

1. Check hybrid-rag-api: `pm2 logs hybrid-rag-api`
2. Check database connection: `psql $POSTGRES_URL -c "SELECT 1;"`
3. Check document count: `psql $POSTGRES_URL -c "SELECT COUNT(*) FROM koi_documents;"`

### Port Conflict on 8400

The content-dashboard uses port 8400 via systemd. If you see a conflict:
```bash
# Check what's using 8400
sudo lsof -i :8400

# If pm2 process exists, remove it
pm2 delete content-dashboard  # if wrongly added

# Use systemd for this service
sudo systemctl restart content-dashboard
```

---

**Last Updated**: 2025-12-31
**Maintainer**: Regen Network DevOps
