# ----------------------------------------------------------------------
# ping command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import asyncio
from typing import Optional, Iterable, List

# Third-party modules
from gufo.ping import Ping

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.validators import is_ipv4
from noc.core.ioloop.util import setup_asyncio, run_sync
from noc.core.perf import metrics
from noc.config import config


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--in", action="append", dest="input", help="File with addresses")
        parser.add_argument(
            "--jobs", action="store", type=int, default=100, dest="jobs", help="Concurrent jobs"
        )
        parser.add_argument("addresses", nargs=argparse.REMAINDER, help="Object name")

    def handle(self, input, addresses, jobs, *args, **options):
        async def runner():
            nonlocal lock
            lock = asyncio.Lock()
            tasks = [
                asyncio.create_task(ping_worker(), name=f"ping-{i}")
                for i in range(min(jobs, len(addr_list)))
            ]
            await asyncio.gather(*tasks)

        async def ping_worker():
            while True:
                async with lock:
                    if not addr_list:
                        break  # Done
                    addr = addr_list.pop(0)
                rtt = await ping.ping(addr)
                if rtt is not None:
                    metrics["address_up"] += 1
                    self.stdout.write(f"{addr} {rtt * 1_000:.2f}ms\n")
                else:
                    metrics["address_down"] += 1
                    self.stdout.write(f"{addr} FAIL\n")

        # Run ping
        addr_list = self.get_addresses(addresses, input)
        lock: Optional[asyncio.Lock] = None
        ping = Ping(tos=config.ping.tos, timeout=1.0)
        setup_asyncio()
        run_sync(runner)
        self.stdout.write(
            f"Stat: down - {metrics.get('address_down').value}; up - {metrics.get('address_up').value}"
        )

    def get_addresses(self, addresses: Iterable[str], input: Iterable[str]) -> List[str]:
        addresses = {a for a in addresses if is_ipv4(a)}
        # Read addresses from files
        if input:
            for fn in input:
                try:
                    with open(fn) as f:
                        addresses.update(line.strip() for line in f if is_ipv4(line.strip()))
                except OSError as e:
                    self.die(f"Cannot read file {fn}: {e}\n")
        return sorted(addresses)


if __name__ == "__main__":
    Command().run()
