# Client Setup and Tuning Instructions

This folder contains scripts for setting up and tuning the client-side system for high-concurrency load testing.

## Files
- `setup.sh`: Initial setup script for installing dependencies and creating the Python environment.
- `tune_server.sh`: Script to tune system settings for high-concurrency networking.

## Running the Scripts
1. Run `sudo bash client/setup.sh` for initial setup (includes tuning).
2. Alternatively, run `sudo bash client/tune_server.sh` for tuning only.
3. Reboot the server after tuning for changes to take full effect.

## Manual Edits (if automated script fails)

If the `tune_server.sh` does not update files properly, make the following manual changes:

1. Edit `/etc/security/limits.conf` (add if not present):
   - `* soft nofile 65536`
   - `* hard nofile 65536`

2. Edit `/etc/sysctl.conf`:
   - `fs.file-max = 2097152`
   - `net.core.somaxconn = 65535`
   - `net.ipv4.ip_local_port_range = 1024 65535`
   - `net.ipv4.tcp_tw_reuse = 1`
   - Then run `sudo sysctl -p`

3. Edit `/etc/systemd/system.conf` and `/etc/systemd/user.conf`:
   - Set `DefaultLimitNOFILE=65536`
   - Then run `sudo systemctl daemon-reload`

## Verification
After running the script or making manual edits, verify the changes:
- Check `/etc/security/limits.conf` for nofile limits.
- Run `sysctl fs.file-max net.core.somaxconn net.ipv4.ip_local_port_range net.ipv4.tcp_tw_reuse` to verify sysctl settings.
- Check `/etc/systemd/system.conf` and `/etc/systemd/user.conf` for DefaultLimitNOFILE.
- Run `ulimit -n` to check current file descriptor limit (may require logout/login for limits.conf changes).

## Troubleshooting
- Ensure the script is run with `sudo`.
- If permissions issues persist, edit files manually as root.
- Reboot after changes for full effect.