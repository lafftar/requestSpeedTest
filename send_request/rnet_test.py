import asyncio
import math
from random import choice
from time import time

import rnet

from utils.custom_log_format import logger
from utils.increase_limits import set_max_open_files

log = logger(name='RNET')
set_max_open_files()
errors = set()
sem = asyncio.Semaphore(100_000)

async def send_request(client, url):
    try:
        async with sem:
            resp = await client.get(url)
        return resp.status.as_int()
    except Exception as e:
        if e not in errors:
            log.error(e)
            errors.add(e)
        raise e


async def test_one_client():
    url = "http://forevercode.online/"
    num_requests = 5000
    t1 = time()
    client = rnet.Client(timeout=60)
    start_time = asyncio.get_event_loop().time()
    tasks = [asyncio.create_task(send_request(client, url)) for _ in range(num_requests)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time
    successful = [r for r in results if not isinstance(r, Exception)]
    num_successful = len(successful)
    req_per_sec = num_successful / duration if duration > 0 else 0

    print(f"rnet: {req_per_sec:.2f} req/sec ({num_successful}/{num_requests} successful)")
    print(f"Statuses: {set(successful)}")
    print(f'Duration: {time() - t1:.2f}s')


async def test_many_clients():
    url = "https://forevercode.online/"
    num_requests = 50_000
    t1 = time()
    clients = [rnet.Client(timeout=60, verify=False, verify_hostname=False)  for _ in range(max(1, math.ceil(num_requests / 500)))]
    start_time = asyncio.get_event_loop().time()
    tasks = [asyncio.create_task(send_request(choice(clients), url)) for _ in range(num_requests)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time
    successful = [r for r in results if not isinstance(r, Exception)]
    num_successful = len(successful)
    req_per_sec = num_successful / duration if duration > 0 else 0

    print(f"rnet: {req_per_sec:.2f} req/sec ({num_successful}/{num_requests} successful)")
    print(f"Statuses: {set(successful)}")
    print(f'Duration: {time() - t1:.2f}s')


if __name__ == "__main__":
    asyncio.run(test_many_clients())
