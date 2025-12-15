module.exports = {
  apps: [{
    name: 'regen-network-api',
    script: 'chatgpt_rest_api_v2.py',
    interpreter: '/opt/projects/regen-python-mcp/venv/bin/python',
    cwd: '/opt/projects/regen-python-mcp',
    env: {
      PORT: 8008,
      HOST: '0.0.0.0',
      PYTHONPATH: '/opt/projects/regen-python-mcp/src'
    },
    error_file: '/opt/projects/regen-python-mcp/logs/pm2-error.log',
    out_file: '/opt/projects/regen-python-mcp/logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    max_memory_restart: '500M',
    restart_delay: 5000,
    autorestart: true,
    watch: false
  }]
};
