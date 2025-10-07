# Server Setup and Tuning Instructions

This folder contains scripts and configurations for setting up and tuning the Nginx server for high concurrency.

## Files
- `startup_script.sh`: Automated script to tune the server and configure Nginx.
- `before_certbot_nginx`: Nginx config template for before running Certbot.

## Manual Edits (if automated script fails)

If the `startup_script.sh` does not update files properly, make the following manual changes:

1. Edit `/etc/nginx/nginx.conf`:
   - Set `worker_processes auto;`
   - In the `events` block, set `worker_connections 65535;`

2. Edit `/etc/security/limits.conf` (add if not present):
   - `* soft nofile 65536`
   - `* hard nofile 65536`

3. Edit `/lib/systemd/system/nginx.service` (in [Service] section):
   - Add `LimitNOFILE=65536`
   - Then run `sudo systemctl daemon-reload`

4. Ensure the site config `/etc/nginx/sites-available/forevercode.online` includes:
   - In the HTTPS server block: `http2_max_concurrent_streams 1000;`

5. After manual edits, run:
   ```
   sudo nginx -t && sudo systemctl restart nginx
   ```

## Verification
After running the script or making manual edits, verify the changes:
- Check `/etc/nginx/nginx.conf` for correct `worker_processes` and `worker_connections`.
- Check `/etc/nginx/sites-available/forevercode.online` for `http2_max_concurrent_streams`.
- Run `sudo nginx -t` to test configuration.
- Monitor logs during load tests for errors.

## Troubleshooting
- Ensure the script is run with `sudo bash startup_script.sh`.
- If permissions issues persist, edit files manually as root.