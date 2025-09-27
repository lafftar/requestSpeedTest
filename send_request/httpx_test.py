import asyncio
import httpx
from httpx import Limits

from utils.custom_log_format import logger

log = logger(name='HTTPX')


async def send_request(client, url):
    try:
        resp = await client.get(url)
        return resp.status_code
    except Exception as e:
        log.exception(e)
        raise e


async def main():
    url = "http://forevercode.online/"
    num_requests = 1000

    async with (
        httpx.AsyncClient(
            timeout=5,
            limits=Limits(max_connections=50_000, max_keepalive_connections=50_000),
            http2=True
                          ) as client):
        start_time = asyncio.get_event_loop().time()
        tasks = [send_request(client, url) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = asyncio.get_event_loop().time()

        duration = end_time - start_time
        successful = [r for r in results if not isinstance(r, Exception)]
        num_successful = len(successful)
        req_per_sec = num_successful / duration if duration > 0 else 0

        print(f"httpx: {req_per_sec:.2f} req/sec ({num_successful}/{num_requests} successful)")
        print(f"Statuses: {set(successful)}")


if __name__ == "__main__":
    asyncio.run(main())
