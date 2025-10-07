# Request Speed Test

A high-throughput HTTP load testing project using the `rnet` library (Rust-based HTTP client with updated TLS settings to bypass WAF checks). This project demonstrates achieving over 20,000 requests per second (RPS) with proper system tuning and client configuration.

I was able to send 10 million requests in 8 minutes:
![](https://i.gyazo.com/d0d9bb7faa22d0619e4d3bd32b3899d7.png)

## Overview

This project explores the limits of HTTP load testing with `rnet`, focusing on:
- Overcoming client-side bottlenecks (file limits, ephemeral ports, connection reuse)
- Server-side tuning for high concurrency (Nginx, kernel parameters)
- Performance scaling across different server configurations
- Error analysis and optimization

## Key Findings

### Client Limitations
- `rnet` does not increase open file limits on Linux, causing failures with bursty requests
- Requires manual tuning for high concurrency

### Performance Results
- **Initial Results**: ~1k RPS on local machine with default settings
- **After Tuning**: 9k RPS on 4vCPU/8GB server
- **Peak Performance**: 20k RPS on 32vCPU dedicated server
- **Stability**: Maintains performance up to 10M+ requests
![](https://i.gyazo.com/2886523dbfa121390b9407d3e38d6d97.png)

### Server Configurations Tested
- 2vCPU/4GB (shared): ~5k RPS
- 4vCPU/8GB (shared): 9k RPS
- 8vCPU (shared): 15k RPS
- 32vCPU (dedicated): 20k RPS

### Common Errors and Fixes
- **File Descriptor Limits**: "Too many open files" → Increase `ulimit` and sysctl `fs.file-max`
- **Ephemeral Port Exhaustion**: "Cannot assign requested address" → Expand `net.ipv4.ip_local_port_range`
- **HTTP/2 GOAWAY**: Server closing connections → Increase `worker_connections` and `http2_max_concurrent_streams`
- **TLS Errors**: Invalid certificate context → Disable verification for testing

### Optimizations Applied
- **Client-Side**:
  - Increased file descriptors to 65k
  - Expanded ephemeral ports to 64k range
  - Enabled TCP TIME_WAIT reuse
  - Adjusted client count for optimal multiplexing (1 client per 100 workers)

- **Server-Side**:
  - Nginx `worker_connections` set to 65k
  - HTTP/2 streams increased to 1k per connection
  - Kernel `somaxconn` set to 65k
  - Systemd limits configured

## Quickstart

### Prerequisites
- Linux server (Ubuntu 25.04 recommended)
- Python 3.13+
- Root access for system tuning

### Setup
1. **Clone and Install**:
   ```bash
   git clone https://github.com/lafftar/requestSpeedTest.git
   cd requestSpeedTest
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install uvloop
   ```

2. **Tune Client System**:
   ```bash
   sudo bash client/tune_server.sh
   sudo reboot  # Required for limits to take effect
   ```

3. **Setup Server (if running on same machine)**:
   ```bash
   sudo bash server/startup_script.sh
   ```

### Running Tests
```bash
source .venv/bin/activate
python -m send_request.rnet_test --total-requests 100000 --concurrency 10000
```

### Example Outputs
- 400k requests: 15k RPS
- 1M requests: 8k RPS (stable)
- 10M requests: Consistent performance

## Project Structure
- `send_request/rnet_test.py`: Main load testing script
- `client/`: Client-side setup and tuning scripts
- `server/`: Server-side Nginx configuration and tuning
- `utils/`: Shared utilities (logging, limits)
- `notes.md`: Detailed findings and test results with screenshots

## Troubleshooting
- If scripts fail, follow manual instructions in `client/README.md` and `server/README.md`
- Ensure `ulimit -n` shows 65536 after reboot
- Check server logs for Nginx errors
- For high concurrency, monitor CPU and memory usage

## Contributing
This project is focused on performance analysis. Contributions for further optimizations or additional HTTP clients welcome.

## License
MIT License