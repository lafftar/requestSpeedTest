import argparse
import asyncio
import itertools
import math
import sys
from collections import Counter
from time import time

import rnet

from utils.custom_log_format import logger
from utils.increase_limits import set_max_open_files

if sys.platform == "linux":
    import uvloop
    uvloop.install()

log = logger(name='RNET')
set_max_open_files()


async def worker(wid, url, clients, counter, total_requests):
    client = clients[wid % len(clients)]
    local_success = 0
    local_fail = 0
    local_statuses = Counter()
    local_errors = Counter()
    while True:
        i = next(counter)
        if i >= total_requests:
            break
        try:
            resp = await client.get(url)
            status = resp.status.as_int() if hasattr(resp, "status") else getattr(resp, "status_code", None)
            local_statuses[status] += 1
            local_success += 1
        except Exception as e:
            name = type(e).__name__
            local_errors[name] += 1
            local_fail += 1
            if local_errors[name] == 1:
                log.error(f"Worker {wid} error: {e}")
    return local_success, local_fail, local_statuses, local_errors


async def run_load_test(url, total_requests, concurrency, clients_count, timeout, verify, verify_hostname):
    clients = [rnet.Client(timeout=timeout, connect_timeout=30, verify=verify, verify_hostname=verify_hostname) for _ in range(clients_count)]
    counter = itertools.count(0)

    t1_wall = time()
    loop = asyncio.get_event_loop()
    t1 = loop.time()
    tasks = [asyncio.create_task(worker(i, url, clients, counter, total_requests)) for i in range(concurrency)]
    results = await asyncio.gather(*tasks)
    t2 = loop.time()
    wall = time() - t1_wall

    success = sum(r[0] for r in results)
    fail = sum(r[1] for r in results)
    statuses = Counter()
    errors = Counter()
    for _, __, st_counter, er_counter in results:
        statuses.update(st_counter)
        errors.update(er_counter)

    duration = max(1e-9, t2 - t1)
    rps = success / duration

    print(f"rnet: {rps:.2f} req/sec ({success}/{total_requests} successful, {fail} failed)")
    print(f"Statuses: {dict(statuses)}")
    if errors:
        print(f"Errors: {dict(errors)}")
    print(f"Duration (event loop): {duration:.3f}s | Wall: {wall:.3f}s")

    return {
        "rps": rps,
        "success": success,
        "fail": fail,
        "statuses": statuses,
        "errors": errors,
        "duration": duration,
        "wall": wall,
    }


def derive_defaults(concurrency, clients):
    if clients is None:
        clients = max(1, math.ceil(concurrency / 10))
    verify = False
    verify_hostname = False
    return clients, verify, verify_hostname


def parse_args():
    parser = argparse.ArgumentParser(description="High throughput rnet load test without spawning 1M tasks.")
    parser.add_argument("--url", type=str, default="https://forevercode.online/", help="Target URL.")
    parser.add_argument("--total-requests", type=int, default=1_000_000, help="Total number of requests to send.")
    parser.add_argument("--concurrency", type=int, default=100_000, help="Concurrent workers (in-flight).")
    parser.add_argument("--clients", type=int, default=None, help="Number of rnet.Client instances to reuse.")
    parser.add_argument("--timeout", type=int, default=60, help="Client timeout seconds.")
    parser.add_argument("--verify", action="store_true", help="Enable TLS verification for HTTPS.")
    parser.add_argument("--verify-hostname", action="store_true", help="Enable TLS hostname verification for HTTPS.")
    return parser.parse_args()


async def main():
    args = parse_args()
    effective_concurrency = max(1, min(args.concurrency, args.total_requests))
    if effective_concurrency != args.concurrency:
        print(f"Adjusted concurrency to {effective_concurrency} (requested {args.concurrency}) for total-requests={args.total_requests}")
    clients_count, default_verify, default_verify_hostname = derive_defaults(effective_concurrency, args.clients)
    verify = args.verify if args.verify else default_verify
    verify_hostname = args.verify_hostname if args.verify_hostname else default_verify_hostname
    await run_load_test(
        url=args.url,
        total_requests=args.total_requests,
        concurrency=effective_concurrency,
        clients_count=args.clients if args.clients is not None else clients_count,
        timeout=args.timeout,
        verify=verify,
        verify_hostname=verify_hostname,
    )


if __name__ == "__main__":
    asyncio.run(main())
