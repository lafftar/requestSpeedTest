# Comprehensive Analysis of rnet: Python HTTP Client with Rust Performance

Based on my deep analysis of all project files, here's a complete understanding of rnet and how it works, with strong emphasis on Python usage since you're intermediate there.

## Project Overview

**rnet** is a blazing-fast Python HTTP client library that combines:
- **Python's ease of use** with **Rust's performance**
- **Browser fingerprinting/emulation** to bypass detection
- **Comprehensive HTTP features** (async/sync, websockets, proxies, etc.)
- **Production-ready** with extensive testing and documentation

## Architecture: How Rust and Python Work Together

### Core Design Pattern
```
Python API (familiar) → PyO3 Bindings → Rust Implementation → wreq HTTP Library
```

### Key Components:

1. **Python Layer** (`python/rnet/`):
   - Clean, type-hinted API similar to `requests`/`httpx`
   - Both async and blocking clients
   - Comprehensive error handling

2. **Rust Core** (`src/`):
   - Uses **tokio** async runtime for performance
   - **wreq** HTTP library for actual network operations
   - **PyO3** for seamless Python integration
   - Memory-safe, high-performance Rust code

3. **Integration Bridge** (`src/rt/mod.rs`):
   - Converts Rust `Future`s to Python `asyncio.Future` objects
   - Maintains Python context across async boundaries
   - Handles task-local storage for proper async behavior

## Complete Python API Reference

### Installation and Setup

```bash
# Install from PyPI
pip install rnet==3.0.0rc6

# Or with asyncio
pip install asyncio rnet==3.0.0rc6

# Development installation
pip install uv maturin
uv venv
source .venv/bin/activate
maturin develop --uv
```

### Basic Usage Patterns

#### Simple GET request:
```python
import asyncio
import rnet

async def main():
    # Quick function call (like requests)
    resp = await rnet.get("https://api.example.com/data")
    data = await resp.json()
    print(data)

asyncio.run(main())
```

#### Client with configuration:
```python
import rnet
from rnet.emulation import Emulation

async def main():
    # Configured client
    client = rnet.Client(
        emulation=Emulation.Chrome137,  # Browser fingerprinting
        timeout=30,
        user_agent="My App/1.0"
    )

    resp = await client.get("https://api.example.com/data")
    print(await resp.text())

asyncio.run(main())
```

### Complete HTTP Methods

All standard HTTP methods are supported with identical signatures:

```python
# All methods available on both client and module level
await client.get(url, **params)
await client.post(url, json=data)
await client.put(url, json=data)
await client.patch(url, json=data)
await client.delete(url)
await client.head(url)
await client.options(url)
await client.trace(url)

# Module-level shortcuts (same as client methods)
await rnet.get(url, **params)
await rnet.post(url, json=data)
await rnet.put(url, json=data)
await rnet.patch(url, json=data)
await rnet.delete(url)
await rnet.head(url)
await rnet.options(url)
await rnet.trace(url)
await rnet.request(method, url, **params)
```

### Complete Request Body Types

#### JSON (automatic serialization):
```python
await client.post(url, json={"key": "value"})
await client.post(url, json={"nested": {"data": [1, 2, 3]}})
```

#### Form data:
```python
await client.post(url, form=[("field", "value")])
await client.post(url, form=[("name", "John"), ("age", "30")])
```

#### Raw text/bytes:
```python
await client.post(url, body="raw text content")
await client.post(url, body=b"raw binary content")
```

#### Files and streams:
```python
# File path
await client.post(url, body=open("file.txt", "rb"))

# Async generator/stream
async def file_stream():
    with open("large_file.zip", "rb") as f:
        while chunk := f.read(8192):
            yield chunk

await client.post(url, body=file_stream())

# Sync generator/stream
def file_stream():
    with open("large_file.zip", "rb") as f:
        while chunk := f.read(8192):
            yield chunk

await client.post(url, body=file_stream())
```

### Complete Response Handling

#### Response object properties:
```python
resp = await client.get(url)

# Status information
print(f"Status: {resp.status}")           # StatusCode object
print(f"Status int: {resp.status.as_int()}")  # 200, 404, etc.
print(f"Is success: {resp.status.is_success()}")  # True for 2xx
print(f"Is error: {resp.status.is_client_error()}")  # True for 4xx
print(f"Is server error: {resp.status.is_server_error()}")  # True for 5xx

# Metadata
print(f"URL: {resp.url}")
print(f"Version: {resp.version}")         # HTTP_11, HTTP_2, HTTP_3
print(f"Headers: {resp.headers}")         # HeaderMap
print(f"Cookies: {resp.cookies}")         # List[Cookie]
print(f"Content-Length: {resp.content_length}")  # Optional[int]
print(f"Remote Address: {resp.remote_addr}")     # Optional[SocketAddr]
print(f"Local Address: {resp.local_addr}")       # Optional[SocketAddr]
print(f"History: {resp.history}")         # List[History] for redirects
print(f"Peer Certificate: {resp.peer_certificate}")  # Optional[bytes]
```

#### Content access methods:
```python
# Text content (with optional encoding)
text = await resp.text()                           # str
text_utf8 = await resp.text_with_charset("utf-8")  # str with specific encoding

# JSON content
json_data = await resp.json()                      # Any (parsed JSON)

# Binary content
bytes_data = await resp.bytes()                    # bytes

# Streaming (memory efficient)
async with resp.stream() as streamer:
    async for chunk in streamer:
        process_chunk(chunk)  # chunk is bytes

# Context manager support
async with resp:
    data = await resp.json()  # Automatic cleanup
```

### Complete Authentication Methods

#### Basic Authentication:
```python
# Tuple format
await client.get(url, basic_auth=("username", "password"))

# With password as None (prompt style)
await client.get(url, basic_auth=("username", None))
```

#### Bearer Token Authentication:
```python
await client.get(url, bearer_auth="your-jwt-token")
```

#### Custom Authorization Header:
```python
await client.get(url, auth="Custom your-token")
await client.get(url, auth="AWS4-HMAC-SHA256 your-creds")
```

#### Custom Headers (alternative):
```python
headers = {"Authorization": "Bearer your-token"}
await client.get(url, headers=headers)
```

### Complete Headers and Cookies Management

#### HeaderMap Usage:
```python
from rnet.header import HeaderMap

# Create and manipulate headers
headers = HeaderMap()
headers.insert("Content-Type", "application/json")
headers.append("Accept", "application/json")
headers.append("Accept", "text/html")

# Access headers
print(headers.get("Content-Type"))          # b"application/json"
print(list(headers.get_all("Accept")))      # [b"application/json", b"text/html"]
print(headers["Content-Type"])              # b"application/json"

# Check existence
print("Content-Type" in headers)            # True
print(headers.contains_key("Content-Type")) # True

# Iteration
for name, value in headers:
    print(f"{name}: {value}")

# Statistics
print(f"Total values: {headers.len()}")    # 3
print(f"Unique keys: {headers.keys_len()}") # 2
print(f"Is empty: {headers.is_empty()}")   # False

# Modification
headers.remove("Accept")                   # Remove all Accept headers
headers.clear()                            # Remove all headers
```

#### OrigHeaderMap (preserves case and order):
```python
from rnet.header import OrigHeaderMap

orig_headers = OrigHeaderMap()
orig_headers.insert("User-Agent")
orig_headers.insert("Accept")
orig_headers.insert("X-Custom-Header")

# Preserves original case and insertion order
for standard_name, original_name in orig_headers:
    print(f"{standard_name} -> {original_name}")
```

#### Cookie Management:
```python
from rnet.cookie import Cookie, Jar

# Create cookies
cookie = Cookie(
    name="session",
    value="abc123",
    domain="example.com",
    path="/",
    secure=True,
    http_only=True,
    max_age=3600  # 1 hour
)

# Cookie jar
jar = Jar()
jar.add_cookie(cookie, "https://example.com")
jar.add_cookie_str("theme=dark; Path=/", "https://example.com")

# Retrieve cookies
session_cookie = jar.get("session", "https://example.com")
all_cookies = jar.get_all()

# Remove cookies
jar.remove("session", "https://example.com")
jar.clear()  # Remove all cookies
```

### Complete Proxy Usage with rnet

#### Basic Proxy Setup

```python
from rnet import Client, Proxy

# HTTP proxy
proxy = Proxy.http("http://proxy.example.com:8080")
client = Client(proxies=[proxy])

# HTTPS proxy
proxy = Proxy.https("https://proxy.example.com:8080")
client = Client(proxies=[proxy])

# SOCKS4 proxy
proxy = Proxy.all("socks4://proxy.example.com:1080")
client = Client(proxies=[proxy])

# SOCKS4a proxy (resolves hostnames)
proxy = Proxy.all("socks4a://proxy.example.com:1080")
client = Client(proxies=[proxy])

# SOCKS5 proxy
proxy = Proxy.all("socks5://proxy.example.com:1080")
client = Client(proxies=[proxy])

# SOCKS5h proxy (resolves hostnames remotely)
proxy = Proxy.all("socks5h://proxy.example.com:1080")
client = Client(proxies=[proxy])
```

#### Proxy Authentication

```python
# Username/password authentication
proxy = Proxy.http(
    "http://proxy.example.com:8080",
    username="myuser",
    password="mypass"
)

# Custom HTTP authentication header
proxy = Proxy.http(
    "http://proxy.example.com:8080",
    custom_http_auth="Basic dXNlcjpwYXNz"  # Base64 encoded
)

# Custom HTTP headers for proxy
proxy = Proxy.http(
    "http://proxy.example.com:8080",
    custom_http_headers={
        "User-Agent": "MyApp/1.0",
        "X-Custom-Header": "value"
    }
)
```

#### Advanced Proxy Configuration

```python
# Multiple proxies (fallback support)
proxies = [
    Proxy.http("http://primary-proxy:8080"),
    Proxy.http("http://backup-proxy:8080")
]
client = Client(proxies=proxies)

# Per-request proxy override
client = Client()  # No default proxy
resp = await client.get(
    "https://api.example.com",
    proxy=Proxy.http("http://request-specific-proxy:8080")
)

# Domain exclusions
proxy = Proxy.all(
    "socks5://proxy.example.com:1080",
    exclusion="google.com,facebook.com,twitter.com"
)
# Requests to excluded domains bypass the proxy
```

#### Proxy with Browser Emulation

```python
from rnet.emulation import Emulation

# Combine proxy with browser fingerprinting
client = Client(
    emulation=Emulation.Chrome137,
    proxies=[Proxy.http("http://proxy.example.com:8080")]
)

# This creates requests that appear to come from Chrome
# but route through your proxy server
```

#### Blocking/Synchronous Proxy Usage

```python
from rnet.blocking import Client, Proxy

# Synchronous proxy usage
client = Client(proxies=[Proxy.http("http://proxy.example.com:8080")])
resp = client.get("https://api.example.com")
print(resp.text())
```

#### Proxy Error Handling

```python
from rnet.exceptions import ConnectionError, TimeoutError

try:
    resp = await client.get("https://api.example.com")
    print(await resp.text())
except ConnectionError as e:
    print(f"Proxy connection failed: {e}")
except TimeoutError as e:
    print(f"Proxy request timed out: {e}")
```

#### Proxy Best Practices

1. **Use SOCKS5** for maximum compatibility
2. **Enable authentication** when required
3. **Test proxy connectivity** before production use
4. **Monitor proxy performance** and rotate if needed
5. **Use domain exclusions** for local/CDN resources
6. **Combine with browser emulation** for stealth scraping

#### Common Proxy Patterns

```python
# Residential proxy rotation
proxy_list = [
    "http://user:pass@proxy1.example.com:8080",
    "http://user:pass@proxy2.example.com:8080",
    "http://user:pass@proxy3.example.com:8080"
]

# Random proxy selection
import random
selected_proxy = Proxy.http(random.choice(proxy_list))
client = Client(proxies=[selected_proxy])

# Geo-targeted proxies
us_proxy = Proxy.http("http://us-proxy.example.com:8080")
eu_proxy = Proxy.http("http://eu-proxy.example.com:8080")

# Route based on target
def get_client_for_region(region):
    if region == "US":
        return Client(proxies=[us_proxy])
    elif region == "EU":
        return Client(proxies=[eu_proxy])
    else:
        return Client()  # No proxy
```

### Complete Browser Emulation System

#### Available Emulations

**Chrome Versions:**
- `Chrome100`, `Chrome101`, `Chrome104`, `Chrome105`, `Chrome106`
- `Chrome107`, `Chrome108`, `Chrome109`, `Chrome110`, `Chrome114`
- `Chrome116`, `Chrome117`, `Chrome118`, `Chrome119`, `Chrome120`
- `Chrome123`, `Chrome124`, `Chrome126`, `Chrome127`, `Chrome128`
- `Chrome129`, `Chrome130`, `Chrome131`, `Chrome132`, `Chrome133`
- `Chrome134`, `Chrome135`, `Chrome136`, `Chrome137`

**Firefox Versions:**
- `Firefox109`, `Firefox117`, `Firefox128`, `Firefox133`, `Firefox135`
- `FirefoxPrivate135`, `FirefoxAndroid135`, `Firefox136`, `FirefoxPrivate136`, `Firefox139`

**Safari Versions:**
- `SafariIos17_2`, `SafariIos17_4_1`, `SafariIos16_5`, `Safari15_3`
- `Safari15_5`, `Safari15_6_1`, `Safari16`, `Safari16_5`, `Safari17_0`
- `Safari17_2_1`, `Safari17_4_1`, `Safari17_5`, `Safari18`, `SafariIPad18`
- `Safari18_2`, `Safari18_3`, `Safari18_3_1`, `Safari18_5`, `SafariIos18_1_1`

**Edge Versions:**
- `Edge101`, `Edge122`, `Edge127`, `Edge131`, `Edge134`

**OkHttp Versions:**
- `OkHttp3_9`, `OkHttp3_11`, `OkHttp3_13`, `OkHttp3_14`
- `OkHttp4_9`, `OkHttp4_10`, `OkHttp4_12`, `OkHttp5`

**Opera Versions:**
- `Opera116`, `Opera117`, `Opera118`, `Opera119`

#### Operating System Support:
- `Windows` - Windows (any version)
- `MacOS` - macOS (any version)
- `Linux` - Linux (any distribution)
- `Android` - Android (mobile)
- `IOS` - iOS (iPhone/iPad)

#### Emulation Usage:

```python
from rnet.emulation import Emulation, EmulationOption, EmulationOS

# Simple emulation
client = Client(emulation=Emulation.Chrome137)

# Advanced configuration
emulation = EmulationOption(
    emulation=Emulation.Firefox139,
    emulation_os=EmulationOS.Windows,
    skip_http2=False,
    skip_headers=False
)
client = Client(emulation=emulation)

# Random emulation for variety
client = Client(emulation=EmulationOption.random())
```

### Complete WebSocket Support

#### Basic WebSocket Connection:
```python
from rnet import Message

# Connect to WebSocket
ws = await client.websocket("wss://echo.example.com")

# Send messages
await ws.send(Message.from_text("Hello!"))
await ws.send(Message.from_json({"type": "ping"}))
await ws.send(Message.from_binary(b"binary data"))
await ws.send(Message.from_ping(b"ping data"))
await ws.send(Message.from_pong(b"pong data"))

# Send multiple messages at once
messages = [
    Message.from_text("Message 1"),
    Message.from_text("Message 2")
]
await ws.send_all(messages)

# Receive messages
while True:
    msg = await ws.recv()
    if msg.text:
        print(f"Received text: {msg.text}")
    elif msg.binary:
        print(f"Received binary: {msg.binary}")
    elif msg.ping:
        print(f"Received ping: {msg.ping}")
    elif msg.pong:
        print(f"Received pong: {msg.pong}")
    elif msg.close:
        code, reason = msg.close
        print(f"Connection closed: {code} - {reason}")
        break

await ws.close()
```

#### WebSocket Configuration:
```python
# Advanced WebSocket options
ws = await client.websocket(
    "wss://api.example.com/ws",
    # Subprotocol negotiation
    protocols=["chat", "superchat"],

    # Buffer sizes
    read_buffer_size=131072,    # 128 KiB
    write_buffer_size=131072,   # 128 KiB
    max_write_buffer_size=1048576,  # 1 MiB

    # Message size limits
    max_message_size=67108864,  # 64 MiB
    max_frame_size=16777216,    # 16 MiB

    # Connection options
    force_http2=True,           # Force HTTP/2 for WebSocket
    accept_unmasked_frames=False,  # RFC compliance

    # Authentication and headers
    headers={"Authorization": "Bearer token"},
    cookies={"session": "abc123"}
)
```

#### WebSocket Properties:
```python
print(f"Status: {ws.status}")
print(f"Version: {ws.version}")
print(f"Headers: {ws.headers}")
print(f"Cookies: {ws.cookies}")
print(f"Remote Address: {ws.remote_addr}")
print(f"Protocol: {ws.protocol}")  # Negotiated subprotocol
```

### Complete Client Configuration Options

#### All Client Parameters:
```python
client = rnet.Client(
    # Emulation
    emulation=Emulation.Chrome137,
    emulation_os=EmulationOS.Windows,

    # User agent
    user_agent="MyApp/1.0",

    # Headers
    headers={"X-Custom": "value"},
    orig_headers=["User-Agent", "Accept"],

    # Referer handling
    referer=True,

    # Redirect handling
    history=True,
    allow_redirects=True,
    max_redirects=10,

    # Cookie management
    cookie_store=True,
    cookie_provider=custom_jar,

    # Timeouts (in seconds)
    timeout=30,
    connect_timeout=10,
    read_timeout=20,

    # TCP options
    tcp_keepalive=60,
    tcp_keepalive_interval=10,
    tcp_keepalive_retries=3,
    tcp_user_timeout=30000,
    tcp_nodelay=True,
    tcp_reuse_address=True,

    # Connection pooling
    pool_idle_timeout=90,
    pool_max_idle_per_host=10,
    pool_max_size=100,

    # Protocol options
    http1_only=False,
    http2_only=False,
    https_only=False,

    # TLS options
    verify=True,
    identity=client_cert,
    keylog=keylog_config,
    tls_info=True,
    min_tls_version=TlsVersion.TLS_1_2,
    max_tls_version=TlsVersion.TLS_1_3,

    # Proxy options
    no_proxy=False,
    proxies=[proxy1, proxy2],

    # Network options
    local_address="192.168.1.100",
    interface="eth0",

    # Compression
    gzip=True,
    brotli=True,
    deflate=True,
    zstd=True,
)
```

### Complete Error Handling

#### All Exception Types:
```python
from rnet.exceptions import (
    # Network errors
    DNSResolverError,
    ConnectionError,
    ConnectionResetError,
    TlsError,

    # HTTP protocol errors
    RequestError,
    StatusError,
    RedirectError,
    TimeoutError,

    # Data processing errors
    BodyError,
    DecodingError,

    # Configuration errors
    BuilderError,

    # WebSocket errors
    UpgradeError,
    WebSocketError,

    # Input validation errors
    URLParseError,

    # System errors
    RustPanic,
)
```

#### Comprehensive Error Handling:
```python
try:
    resp = await client.get(url)
    resp.raise_for_status()  # Like requests

    # Additional status checks
    if resp.status.is_client_error():
        print("Client error occurred")
    elif resp.status.is_server_error():
        print("Server error occurred")

    data = await resp.json()

except TimeoutError as e:
    print(f"Request timed out: {e}")
    # Retry logic here

except ConnectionError as e:
    print(f"Connection failed: {e}")
    # Connection recovery logic

except TlsError as e:
    print(f"TLS error: {e}")
    # Certificate/validation issues

except StatusError as e:
    print(f"HTTP error {e.status_code}: {e}")
    # HTTP error handling

except DecodingError as e:
    print(f"Content decoding failed: {e}")
    # Encoding/charset issues

except rnet.exceptions.RequestError as e:
    print(f"Request failed: {e}")
    # General request errors

except Exception as e:
    print(f"Unexpected error: {e}")
    # Fallback error handling
```

### Complete Multipart Uploads

#### Multipart Form Creation:
```python
from rnet import Multipart, Part
from pathlib import Path

# Create multipart form
multipart = Multipart(
    # Text part
    Part(
        name="title",
        value="My Document",
        filename="title.txt",
        mime="text/plain"
    ),

    # Binary data part
    Part(
        name="data",
        value=b"binary content",
        filename="data.bin",
        mime="application/octet-stream"
    ),

    # File part
    Part(
        name="document",
        value=Path("document.pdf"),
        filename="document.pdf",
        mime="application/pdf"
    ),

    # Stream part
    Part(
        name="large_file",
        value=file_stream_generator(),
        filename="large.zip",
        mime="application/zip",
        length=1024000  # Content length for streams
    ),

    # Part with custom headers
    Part(
        name="custom",
        value="custom content",
        headers=HeaderMap({"X-Custom": "value"})
    )
)

# Send multipart request
resp = await client.post(url, multipart=multipart)
```

### Complete Streaming Operations

#### Request Streaming:
```python
# Large file upload with streaming
async def file_stream():
    with open("large_file.zip", "rb") as f:
        while chunk := f.read(8192):  # 8KB chunks
            yield chunk

resp = await client.post(
    url,
    body=file_stream(),
    headers={"Content-Type": "application/zip"}
)

# Generator with custom chunking
def custom_stream(data_source):
    buffer = bytearray(4096)
    while True:
        bytes_read = data_source.readinto(buffer)
        if bytes_read == 0:
            break
        yield bytes(buffer[:bytes_read])

resp = await client.post(url, body=custom_stream(file_obj))
```

#### Response Streaming:
```python
# Memory-efficient large file download
resp = await client.get(large_file_url)

async with resp.stream() as streamer:
    with open("downloaded_file.zip", "wb") as f:
        async for chunk in streamer:
            f.write(chunk)
            # Process chunk if needed
            print(f"Downloaded {len(chunk)} bytes")
```

### Complete TLS and Certificate Management

#### TLS Version Control:
```python
from rnet.tls import TlsVersion

client = Client(
    min_tls_version=TlsVersion.TLS_1_2,
    max_tls_version=TlsVersion.TLS_1_3
)
```

#### Client Certificates:
```python
from rnet.tls import Identity

# PKCS#12 format
identity = Identity.from_pkcs12_der(
    cert_data,  # bytes
    "password"  # str
)

# PEM format
identity = Identity.from_pkcs8_pem(
    cert_pem,  # bytes
    key_pem    # bytes
)

client = Client(identity=identity)
```

#### Custom Certificate Stores:
```python
from rnet.tls import CertStore

# From DER certificates
cert_store = CertStore.from_der_certs([cert1, cert2])

# From PEM certificates
cert_store = CertStore.from_pem_certs(["cert1.pem", "cert2.pem"])

# From PEM stack
cert_store = CertStore.from_pem_stack(pem_data)

# With system certificates
cert_store = CertStore(
    der_certs=[custom_cert],
    default_paths=True  # Include system certs
)

client = Client(verify=cert_store)
```

#### TLS Key Logging:
```python
from rnet.tls import KeyLog

# Use SSLKEYLOGFILE environment variable
keylog = KeyLog.environment()

# Custom file path
keylog = KeyLog.file(Path("/path/to/keylog.txt"))

client = Client(keylog=keylog)
```

### Complete Blocking/Synchronous Usage

#### Blocking Client:
```python
from rnet.blocking import Client

# Synchronous client (no asyncio needed)
client = Client(
    timeout=30,
    emulation=Emulation.Chrome137
)

# All methods work synchronously
resp = client.get("https://api.example.com")
print(resp.text())  # Direct access, no await

resp = client.post("https://api.example.com", json={"key": "value"})
data = resp.json()  # Direct access

# Context manager support
with client.get(url) as resp:
    print(resp.status)
    print(resp.text())
```

#### Blocking WebSocket:
```python
from rnet.blocking import Client

client = Client()
ws = client.websocket("wss://echo.example.com")

with ws:
    ws.send(Message.from_text("Hello!"))
    msg = ws.recv()
    print(f"Received: {msg.text}")
    ws.close()
```

### Complete Query Parameters and URL Encoding

#### Query Parameters:
```python
# List of tuples
query_params = [
    ("search", "python http client"),
    ("limit", "10"),
    ("sort", "relevance")
]

resp = await client.get(url, query=query_params)

# Dictionary (converted to list of tuples)
query_dict = {"search": "python", "limit": 10}
resp = await client.get(url, query=list(query_dict.items()))
```

### Complete Redirect Handling

#### Redirect Configuration:
```python
# Follow redirects (default)
resp = await client.get(url, allow_redirects=True, max_redirects=5)

# Don't follow redirects
resp = await client.get(url, allow_redirects=False)

# Custom redirect limit
resp = await client.get(url, max_redirects=3)

# Store redirect history
client = Client(history=True)
resp = await client.get(url)
for redirect in resp.history:
    print(f"{redirect.status} -> {redirect.url}")
    print(f"Previous: {redirect.previous}")
    print(f"Headers: {redirect.headers}")
```

### Complete Compression Support

#### All Compression Algorithms:
```python
client = Client(
    gzip=True,      # GNU zip compression
    brotli=True,    # Brotli compression
    deflate=True,   # DEFLATE compression
    zstd=True       # Zstandard compression
)

# Automatic decompression
resp = await client.get(compressed_url)
text = await resp.text()  # Automatically decompressed
```

### Complete Connection Pooling

#### Pool Configuration:
```python
client = Client(
    # Connection pool settings
    pool_idle_timeout=90,        # Idle timeout in seconds
    pool_max_idle_per_host=10,   # Max idle connections per host
    pool_max_size=100,           # Max total connections

    # TCP keepalive
    tcp_keepalive=60,            # Keepalive interval
    tcp_keepalive_interval=10,   # Keepalive probe interval
    tcp_keepalive_retries=3,     # Max keepalive retries

    # TCP options
    tcp_nodelay=True,            # Disable Nagle's algorithm
    tcp_reuse_address=True,      # Reuse addresses
    tcp_user_timeout=30000,      # User timeout in milliseconds
)
```

### Performance Characteristics

#### Benchmark Results (from CSV data):

**Sync Performance (20k payload):**
- rnet: 0.08s (session), 0.13s (non-session)
- pycurl: 0.08s (session), 0.14s (non-session)
- curl_cffi: 0.13s (session), 0.19s (non-session)
- requests: 0.23s (session), 0.34s (non-session)

**Async Performance (20k payload):**
- rnet: 0.03s (session), 0.17s (non-session)
- aiohttp: 0.04s (session), 0.20s (non-session)
- curl_cffi: 0.09s (session), 0.24s (non-session)

**Threaded Performance (20k payload, 8 threads):**
- rnet: 0.02s (session), 0.04s (non-session)
- pycurl: 0.02s (session), 0.03s (non-session)
- curl_cffi: 0.13s (session), 0.15s (non-session)

#### Why It's Fast:
1. **Rust Core**: Memory-safe, zero-cost abstractions
2. **Async by Default**: Non-blocking I/O with tokio
3. **Connection Pooling**: Reuses connections efficiently
4. **HTTP/2 Support**: Multiplexed requests
5. **Optimized TLS**: BoringSSL integration
6. **Zero-copy Operations**: Where possible

#### Memory Management:
- **Zero-copy** transfers for large payloads
- **Streaming** for memory-efficient processing
- **Efficient buffering** in Rust layer
- **Automatic cleanup** via PyO3 reference counting

### Integration Patterns

#### With Existing Python Code:
```python
# Drop-in replacement for requests
# import requests → import rnet
# requests.get() → await rnet.get()

# With aiohttp-style async
async def fetch_data():
    async with rnet.Client() as client:  # Context manager support
        resp = await client.get(url)
        return await resp.json()
```

#### With Web Frameworks:
```python
# FastAPI example
from fastapi import FastAPI
import rnet

app = FastAPI()

@app.get("/proxy/{url:path}")
async def proxy_request(url: str):
    # Fast proxying with rnet
    resp = await rnet.get(f"https://{url}")
    return await resp.json()

# Django view example
import asyncio
from django.http import JsonResponse
import rnet

async def api_proxy(request, endpoint):
    # Async view with rnet
    resp = await rnet.get(f"https://api.example.com/{endpoint}")
    data = await resp.json()
    return JsonResponse(data)
```

#### With Async Libraries:
```python
# With asyncio.gather for concurrent requests
async def fetch_multiple(urls):
    async with rnet.Client() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [await resp.json() for resp in responses]

# With asyncio.Queue for rate limiting
async def rate_limited_requests(urls, rate_limit=10):
    queue = asyncio.Queue()
    for url in urls:
        await queue.put(url)

    async def worker():
        async with rnet.Client() as client:
            while True:
                url = await queue.get()
                try:
                    resp = await client.get(url)
                    yield await resp.json()
                finally:
                    queue.task_done()

    # Create workers
    workers = [asyncio.create_task(worker()) for _ in range(rate_limit)]
    await queue.join()
    for w in workers:
        w.cancel()
```

### Testing and Reliability

#### Test Coverage:
The project includes comprehensive tests covering:
- All HTTP methods and status codes
- Authentication mechanisms (Basic, Bearer, Custom)
- Compression algorithms (gzip, brotli, deflate, zstd)
- Header and cookie handling
- Multipart uploads with files and streams
- WebSocket communication (text, binary, ping/pong)
- Error conditions and edge cases
- Streaming operations (request/response)
- Redirect handling and history
- TLS certificate validation
- Proxy configurations
- Browser emulation accuracy

#### Test Categories:
```python
# Request testing
test_gzip()           # Compression
test_auth()           # Authentication
test_bearer_auth()    # Bearer tokens
test_basic_auth()     # Basic auth
test_send_headers()   # Headers
test_send_cookies()   # Cookies
test_send_form()      # Form data
test_send_json()      # JSON payloads
test_send_text()      # Text content
test_send_bytes()     # Binary content
test_send_async_bytes_stream()  # Async streaming
test_send_sync_bytes_stream()   # Sync streaming

# Response testing
test_get_cookies()    # Cookie parsing
test_get_headers()    # Header access
test_getters()        # Response properties
test_get_json()       # JSON parsing
test_get_text()       # Text decoding
test_get_bytes()      # Binary content
test_get_stream()     # Streaming responses
test_peer_certificate()  # TLS certificates

# Header testing
test_construction_and_is_empty()
test_insert_and_get()
test_append_and_get_all()
test_remove_and_delitem()
test_setitem_and_getitem()
test_len_and_keys_len()
test_clear()
test_iter()
test_edge_cases()
test_get_with_default()
test_init_with_dict()
```

### Build and Development

#### Building from Source:
```bash
# Install build dependencies (Ubuntu/Debian)
sudo apt install -y build-essential cmake perl pkg-config libclang-dev musl-tools git
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
pip install uv maturin

# Create virtual environment
uv venv
source .venv/bin/activate

# Development build
maturin develop --uv

# Release build
maturin build --release

# Build wheels
maturin build --release
```

#### Musl Cross-Compilation:
```bash
# For different architectures
bash .github/musl_build.sh i686-unknown-linux-musl
bash .github/musl_build.sh x86_64-unknown-linux-musl
bash .github/musl_build.sh aarch64-unknown-linux-musl
bash .github/musl_build.sh armv7-unknown-linux-musleabihf
```

#### Platform Support:
- **Linux**: glibc >= 2.34 (x86_64, aarch64, armv7, i686), musl (x86_64, aarch64, armv7, i686)
- **macOS**: x86_64, aarch64
- **Windows**: x86_64, i686, aarch64

### When to Use rnet

#### Perfect for:
- High-performance web scraping with browser emulation
- API clients requiring stealth and fingerprinting bypass
- Applications needing both sync and async support
- Memory-constrained environments
- Production systems requiring reliability
- Large-scale data collection
- Real-time applications with WebSocket support

#### Less ideal for:
- Simple scripts (use `requests` for simplicity)
- When you need extensive middleware/plugins
- Pure Python environments (no Rust compilation)
- Applications where build complexity is an issue

### Key Takeaways for Python Developers

1. **API Familiarity**: If you know `requests` or `httpx`, you'll feel at home
2. **Performance**: Rust speed with Python ergonomics - outperforms most Python HTTP clients
3. **Browser Evasion**: Built-in fingerprinting to avoid detection
4. **Comprehensive**: Supports everything from simple GETs to complex WebSocket apps
5. **Production Ready**: Extensive testing, error handling, and documentation
6. **Memory Efficient**: Streaming and zero-copy operations for large payloads
7. **Async First**: Designed for high-performance async applications

The Rust implementation handles all the performance-critical networking code while exposing a clean, Pythonic API that feels natural to use. You get the best of both worlds: Python's ease of development with Rust's runtime performance and memory safety.

### Complete Example Applications

#### Web Scraper with Browser Emulation:
```python
import asyncio
import rnet
from rnet.emulation import Emulation

async def scrape_with_emulation(urls):
    async with rnet.Client(
        emulation=Emulation.Chrome137,
        timeout=30,
        proxies=[Proxy.http("http://proxy.example.com:8080")]
    ) as client:
        for url in urls:
            try:
                resp = await client.get(url)
                if resp.status.is_success():
                    content = await resp.text()
                    # Process scraped content
                    print(f"Scraped {len(content)} chars from {url}")
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")

asyncio.run(scrape_with_emulation(url_list))
```

#### API Client with Automatic Retries:
```python
import asyncio
import rnet
from rnet.exceptions import TimeoutError, ConnectionError

async def robust_api_call(url, max_retries=3):
    async with rnet.Client(timeout=10) as client:
        for attempt in range(max_retries):
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                return await resp.json()
            except (TimeoutError, ConnectionError) as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except rnet.exceptions.StatusError as e:
                if e.status_code >= 500:  # Server error, retry
                    if attempt == max_retries - 1:
                        raise e
                    await asyncio.sleep(2 ** attempt)
                else:  # Client error, don't retry
                    raise e

data = await robust_api_call("https://api.example.com/data")
```

#### Real-time WebSocket Application:
```python
import asyncio
import json
import rnet
from rnet import Message

async def websocket_chat_client(server_url, username):
    async with rnet.Client() as client:
        ws = await client.websocket(server_url)

        # Send join message
        join_msg = {"type": "join", "username": username}
        await ws.send(Message.from_json(join_msg))

        # Handle incoming messages
        async def receive_messages():
            while True:
                msg = await ws.recv()
                if msg.text:
                    data = json.loads(msg.text)
                    if data["type"] == "message":
                        print(f"{data['username']}: {data['content']}")
                    elif data["type"] == "system":
                        print(f"System: {data['content']}")
                elif msg.close:
                    break

        # Send user input
        async def send_messages():
            while True:
                text = await asyncio.get_event_loop().run_in_executor(
                    None, input, "Message: "
                )
                if text.lower() == "quit":
                    await ws.close()
                    break

                msg = {"type": "message", "content": text}
                await ws.send(Message.from_json(msg))

        await asyncio.gather(receive_messages(), send_messages())

asyncio.run(websocket_chat_client("wss://chat.example.com", "user123"))
```

This comprehensive guide covers every aspect of rnet, from basic usage to advanced features, with complete examples and performance data. The documentation is designed to be a complete reference that AI systems can use to understand and work with rnet effectively.