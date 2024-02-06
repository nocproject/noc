# ----------------------------------------------------------------------
# device-discovery command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import asyncio
import socket
from typing import Optional, Iterable, List, Dict
from collections import defaultdict

# Third-party modules
from gufo.ping import Ping

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.core.validators import is_ipv4
from noc.core.ioloop.util import setup_asyncio, run_sync
from noc.core.perf import metrics
from noc.core.ip import IP
from noc.config import config
from noc.core.checkers.loader import loader
from noc.core.checkers.base import Check, Checker
from noc.core.checkers.snmp import SUGGEST_CHECK
from noc.core.checkers.tcp import TCP_DIAG
from noc.core.script.scheme import SNMPCredential, SNMPv3Credential
from noc.main.models.pool import Pool
from noc.core.purgatorium import ProtocolCheckResult, register

checker_cache = {}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--in", action="append", dest="input", help="File with addresses")
        parser.add_argument(
            "--pool",
            action="store",
            dest="pool",
            default="default",
            help="NOC Pool on scanning net",
        )
        parser.add_argument(
            "--jobs", action="store", type=int, default=100, dest="jobs", help="Concurrent jobs"
        )
        parser.add_argument(
            "--dry-run", dest="dry_run", action="store_true", help="Test only. Do not save records"
        ),
        parser.add_argument("--ports", action="store", type=str, help="Check TCP ports")
        parser.add_argument(
            "--check",
            action="store",
            dest="checks",
            help="Additional custom checks",
            default="icmp",
        )
        parser.add_argument(
            "--community", action="store", help="Run SNMP v2 check", default="public"
        )
        # user:sha:1234:des:4536
        parser.add_argument(
            "--snmp-user", action="store", dest="snmp_user", help="Run SNMP v3 check", default=""
        )
        parser.add_argument("addresses", nargs=argparse.REMAINDER, help="Object name")

    @staticmethod
    def parse_checks(
        address: str,
        checks: Optional[str] = None,
        ports: Optional[str] = None,
        community: Optional[str] = None,
        snmp_user: Optional[str] = None,
    ) -> Iterable[Check]:
        """
        Parse required checks
        tcp://*:80
        """
        for p in (ports or "").split(","):
            try:
                p = int(p.strip())
            except ValueError:
                continue
            yield Check(name=TCP_DIAG, address=address, port=p)
        snmp_cred = []
        for c in (community or "").split(","):
            snmp_cred.append(SNMPCredential(snmp_ro=c))
        for c in (snmp_user or "").split(","):
            # user:sha:123456:des:123457
            creds = {}
            username, *other = c.split(":")
            creds["username"] = username
            if len(other) >= 2:
                # authNoPriv
                creds.update({"auth_proto": other[0], "auth_key": other[1]})
            if len(other) > 2:
                # authPriv
                creds.update({"private_proto": other[2], "private_key": other[3]})
            snmp_cred.append(SNMPv3Credential(**creds))
        if snmp_cred:
            yield Check(
                SUGGEST_CHECK,
                address=address,
                credentials=snmp_cred,
            )
        for c in checks.split(";"):
            name, *other = c.split("?")
            if not other:
                yield Check(name=name, address=address)
                continue
            other = dict(x.split("=") for x in other[0].split(","))
            yield Check(
                name=name,
                address=address,
                port=int(other["port"]) if "port" in other else None,
                credentials=snmp_cred,
            )

    def handle(
        self,
        input,
        addresses,
        jobs,
        checks,
        pool: str,
        ports: Optional[str] = None,
        community: Optional[str] = None,
        snmp_user: Optional[str] = None,
        dry_run: bool = False,
        *args,
        **options,
    ):
        async def runner():
            nonlocal lock
            lock = asyncio.Lock()
            tasks = [
                asyncio.create_task(check_worker(), name=f"check-{i}")
                for i in range(min(jobs, len(addr_list)))
            ]
            await asyncio.gather(*tasks)

        async def check_worker():
            while True:
                async with lock:
                    if not addr_list:
                        break  # Done
                    addr = addr_list.pop(0)
                rtt = await ping.ping(addr)
                if rtt is None:
                    metrics["address_down"] += 1
                    self.stdout.write(f"{addr} FAIL\n")
                    continue
                result[addr].append(
                    ProtocolCheckResult(
                        check="ICMP",
                        status=True,
                        available=True,
                    )
                )
                metrics["address_up"] += 1
                # SNMP/HTTP/Agent/TCP Check
                for c in self.parse_checks(addr, checks, ports, community, snmp_user):
                    h = self.get_checker(c.name)
                    if not h:
                        continue
                    for r in h.iter_result([c]):
                        # print(f"[{c.name}] Result: {r}")
                        # self.stdout.write(f"{addr} Port {r.port} is open\n")
                        if r.skipped:
                            continue
                        result[addr].append(
                            ProtocolCheckResult(
                                check=r.check,
                                status=r.status,
                                port=r.port,
                                available=r.is_available,
                                access=r.is_access,
                                error=r.error,
                            )
                        )
                self.print_out(addr, rtt, result[addr])

        socket.setdefaulttimeout(2)
        result: Dict[str, List[ProtocolCheckResult]] = defaultdict(list)

        addr_list = self.get_addresses(addresses, input)
        lock: Optional[asyncio.Lock] = None
        ping = Ping(tos=config.ping.tos, timeout=1.0)
        setup_asyncio()
        run_sync(runner)
        downs = metrics.get("address_down").value if metrics.get("address_down") else 0
        ups = metrics.get("address_up").value if metrics.get("address_up") else 0
        self.stdout.write(f"Stat: down - {downs}; up - {ups}\n")
        if dry_run:
            return
        pool = self.get_pool(pool=pool)
        for address, checks in result.items():
            register(
                address,
                pool,
                "network-scan",
                checks=checks,
            )

    @staticmethod
    def get_pool(pool: str) -> int:
        """
        Return pool bi_id
        """
        if pool.isalnum():
            return int(pool)
        connect()

        p = Pool.get_by_name(pool)
        if not p:
            raise ValueError("Unknown pool: %s" % pool)
        return p.bi_id

    @staticmethod
    def get_checker(name: str) -> Checker:
        """
        Return checker function by name
        """
        global checker_cache

        if name not in checker_cache:
            h = loader[name]
            checker_cache[name] = h() if h else None
        return checker_cache[name]

    def get_addresses(self, addresses: Iterable[str], input: Iterable[str]) -> List[str]:
        r = set()
        for a in addresses:
            # if not is_ipv4(a):
            #    continue
            a = IP.prefix(a)
            if a.size == 1:
                r.add(a)
                continue
            for x in a.iter_address(count=a.size):
                r.add(x)
        # Read addresses from files
        if input:
            for fn in input:
                try:
                    with open(fn) as f:
                        r.update(line.strip() for line in f if is_ipv4(line.strip()))
                except OSError as e:
                    self.die(f"Cannot read file {fn}: {e}\n")
        return [x.address for x in sorted(r)]

    def print_out(self, address: str, rtt: float, checks: List[ProtocolCheckResult]):
        """
        Format out result
        """
        r = []
        for c in checks:
            r.append(f"{c.check}:{c.port} {'OK' if c.status else 'FAIL'}")
        self.stdout.write(
            f"{address} {rtt * 1_000:.2f}ms| {';'.join('%s:%s %s' % (c.check, c.port or '', 'OK' if c.status else 'FAIL') for c in checks)}\n"
        )


if __name__ == "__main__":
    Command().run()
