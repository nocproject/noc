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
from typing import Optional, Iterable, List, Tuple, Union, Dict, Any

# Third-party modules
import progressbar
from gufo.ping import Ping

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.core.validators import is_ipv4
from noc.core.ioloop.util import run_sync
from noc.core.perf import metrics
from noc.core.ip import IP
from noc.config import config
from noc.core.checkers.loader import loader
from noc.core.checkers.base import Check, Checker, DataItem, TCP_CHECK
from noc.services.activator.checkers.snmp import SNMPProtocolChecker, SUGGEST_CHECK
from noc.core.script.scheme import SNMPCredential, SNMPv3Credential, Protocol
from noc.core.purgatorium import ProtocolCheckResult, register
from noc.core.mib import mib

checker_cache = {}
HOSTNAME_OID = mib["SNMPv2-MIB::sysName", 0]
DESCR_OID = mib["SNMPv2-MIB::sysDescr", 0]
UPTIME_OID = mib["SNMPv2-MIB::sysUpTime", 0]
CHASSIS_OID = mib["IF-MIB::ifPhysAddress", 1]
OIDS = [mib["SNMPv2-MIB::sysObjectID", 0], HOSTNAME_OID, DESCR_OID, UPTIME_OID, CHASSIS_OID]
SOCKET_DEFAULT_TIMEOUT = 2
ICMP_DIAG = "ICMP"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--in", action="append", dest="input", help="File with addresses")
        parser.add_argument(
            "--pool",
            action="store",
            dest="pool",
            default="default",
            help="NOC Pool on scanning net",
            required=True,
        )
        parser.add_argument(
            "--adm-domain",
            action="store",
            dest="adm_domain",
            default="default",
            help="NOC Administrative Domain on scanning net",
            required=False,
        )
        parser.add_argument(
            "--labels",
            action="store",
            dest="labels",
            help="Labels list, separate by comma",
            required=False,
        )
        parser.add_argument(
            "--jobs", action="store", type=int, default=100, dest="jobs", help="Concurrent jobs"
        )
        parser.add_argument(
            "--dry-run", dest="dry_run", action="store_true", help="Test only. Do not save records"
        ),
        parser.add_argument(
            "--print-out", dest="print_out", action="store_true", help="Printing result to output"
        ),
        parser.add_argument(
            "--print-file", dest="print_file", help="Printing result to file output"
        ),
        parser.add_argument(
            "--ip-scan",
            dest="ip_scan",
            action="store_true",
            help="Address wit prefixes enabled IP Scan",
        ),
        parser.add_argument("--ports", action="store", type=str, help="Check TCP ports")
        parser.add_argument("--rule", action="store", type=str, help="Check Rule. Set rule name")
        parser.add_argument(
            "--check",
            action="store",
            dest="checks",
            help="Additional custom checks",
            default="icmp",
        )
        parser.add_argument(
            "--community",
            action="store",
            help="Run SNMP v2 check",  # default="public"
        )
        # user:sha:1234:des:4536
        parser.add_argument(
            "--snmp-user", action="store", dest="snmp_user", help="Run SNMP v3 check", default=""
        )
        parser.add_argument("addresses", nargs=argparse.REMAINDER, help="Object name")

    def handle(
        self,
        input,
        addresses,
        jobs,
        checks,
        pool: str,
        adm_domain: Optional[str] = None,
        labels: Optional[str] = None,
        ports: Optional[str] = None,
        community: Optional[str] = None,
        snmp_user: Optional[str] = None,
        dry_run: bool = False,
        print_out: bool = False,
        print_file: Optional[str] = None,
        ip_scan: bool = False,
        rule: Optional[str] = None,
        *args,
        **options,
    ):
        """Processed settings"""

        async def runner():
            nonlocal lock
            lock = asyncio.Lock()

            if not dry_run:
                queue = asyncio.Queue()
                loop = asyncio.get_running_loop()
                loop.create_task(self.register_data(pool, queue))
            else:
                queue = None
            tasks = [
                asyncio.create_task(
                    self.check_worker(
                        queue, lock, addr_list, checks, ports, bar, print_out=print_out
                    ),
                    name=f"check-{i}",
                )
                for i in range(min(jobs, len(addr_list)))
            ]
            await asyncio.gather(*tasks)
            if queue:
                queue.put_nowait(None)

        addr_list = self.get_addresses(addresses, input, rule, ip_scan)
        lock: Optional[asyncio.Lock] = None
        socket.setdefaulttimeout(SOCKET_DEFAULT_TIMEOUT)
        pool = self.get_pool(pool=pool)
        # SNMP Checker
        snmp_creds = self.parse_credentials(community, snmp_user)
        if snmp_creds:
            self.get_checker(SUGGEST_CHECK, rules=snmp_creds)
            self.print("SNMP Credentials: %s", snmp_creds)
        # result = defaultdict(lambda: {"checks": [], "source": "network-scan", "data": {}})
        with progressbar.ProgressBar(max_value=len(addr_list)) as bar:
            run_sync(runner)
        downs = metrics.get("address_down").value if metrics.get("address_down") else 0
        ups = metrics.get("address_up").value if metrics.get("address_up") else 0
        self.stdout.write(
            f"\nStat: down - {downs}; up - {ups}; SNMP up - {metrics['address_snmp_up'].value}\n"
        )

    async def check_worker(
        self,
        queue: Optional[asyncio.Queue],
        lock: asyncio.Lock,
        addr_list: List[str],
        checks: str,
        ports: str,
        bar: progressbar.ProgressBar,
        print_out: bool = False,
        name: str = "check",
    ):
        """
        Scan worker
        """
        ping = self.get_checker(ICMP_DIAG)
        snmp_checker = self.get_checker(SUGGEST_CHECK)
        while True:
            async with lock:
                if not addr_list:
                    break  # Done
                addr = addr_list.pop(0)
            rtt = await ping.ping(addr)
            if rtt is None:
                metrics["address_down"] += 1
                metrics["address_all"] += 1
                if print_out:
                    self.stdout.write(f"{addr} FAIL\n")
                bar.update(metrics["address_all"].value)
                continue
            params = {
                "checks": [ProtocolCheckResult(check=ICMP_DIAG, status=True, available=True)],
                "source": "network-scan",
                "address": addr,
            }
            metrics["address_up"] += 1
            snmp_cred = None
            if snmp_checker:
                # for r in snmp_checker.iter_result([Check(SUGGEST_CHECK, address=addr)]):
                async for r in snmp_checker.iter_result_async([Check(SUGGEST_CHECK, address=addr)]):
                    if r.status and not snmp_cred:
                        metrics["address_snmp_up"] += 1
                    if r.credential:
                        snmp_cred = r.credential
                    # data = {}
                    # if r.data:
                    #    data = self.parse_data(addr, r.data)
                    params["checks"].append(
                        ProtocolCheckResult(
                            check=r.check,
                            status=r.status,
                            port=r.port,
                            available=r.error.is_available if r.error else True,
                            access=r.error.is_access if r.error else True,
                            data=self.parse_data(r.data, params),
                            error=r.error.message if r.error else "",
                        )
                    )
            # SNMP/HTTP/Agent/TCP Check
            for c in self.parse_checks(addr, checks, ports, snmp_cred):
                h = self.get_checker(c.name)
                if not h or ICMP_DIAG in h.CHECKS:
                    continue
                async for r in h.iter_result_async([c]):
                    # print(f"[{c.name}] Result: {r}")
                    # self.stdout.write(f"{addr} Port {r.port} is open\n")
                    if r.skipped:
                        continue
                    error, is_available, is_access = "", r.status, r.status
                    if r.error:
                        error, is_available, is_access = (
                            r.error.message,
                            r.error.is_available,
                            r.error.is_access,
                        )
                    params["checks"].append(
                        ProtocolCheckResult(
                            check=r.check,
                            status=r.status,
                            port=r.port,
                            available=is_available,
                            access=is_access,
                            data=self.parse_data(r.data, params),
                            error=error,
                        )
                    )
            metrics["address_all"] += 1
            bar.update(metrics["address_all"].value)
            if queue:
                queue.put_nowait(params)
            if print_out:
                self.print_out(addr, rtt, params["checks"])

    async def register_data(self, pool, queue):
        self.print("Run register data task")
        while True:
            item = await queue.get()
            if item:
                item["pool"] = pool
                register(**item)
            else:
                self.print("End Register data")
                break

    @staticmethod
    def get_pool(pool: str) -> int:
        """
        Return pool bi_id
        """
        if pool.isdigit():
            return int(pool)

        from noc.main.models.pool import Pool

        connect()

        p = Pool.get_by_name(pool)
        if not p:
            raise ValueError("Unknown pool: %s" % pool)
        return p.bi_id

    @staticmethod
    def get_checker(name: str, **kwargs) -> Optional[Checker]:
        """
        Return checker function by name
        """
        global checker_cache

        if name in checker_cache:
            return checker_cache[name]
        elif name == ICMP_DIAG:
            checker_cache[name] = Ping(tos=config.ping.tos, timeout=1.0)
        elif name == SUGGEST_CHECK and kwargs:
            checker_cache[SUGGEST_CHECK] = SNMPProtocolChecker(**kwargs)
        else:
            h = loader[name]
            checker_cache[name] = h(**kwargs) if h else None
        return checker_cache[name]

    def get_addresses(
        self,
        addresses: Iterable[str],
        input: Iterable[str],
        rule: Optional[Any] = None,
        ip_scan: bool = False,
    ) -> List[str]:
        """Getting addresses for net-scan"""
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
        if rule:
            for a in self.iter_address_rule(rule):
                r.add(a)
        # Read addresses from files
        if input:
            for fn in input:
                try:
                    with open(fn) as f:
                        r.update(IP.prefix(line.strip()) for line in f if is_ipv4(line.strip()))
                except OSError as e:
                    self.die(f"Cannot read file {fn}: {e}\n")
        if ip_scan:
            for a in self.iter_address_scan():
                r.add(a)
        return [x.address for x in sorted(r)]

    @classmethod
    def iter_address_rule(cls, rule: str) -> Iterable[IP]:
        """Iterate over addresses set on rules"""
        from noc.sa.models.objectdiscoveryrule import ObjectDiscoveryRule

        connect()
        rule = ObjectDiscoveryRule.objects.get(name=rule)
        if not rule:
            print(f"Unknown Object Discovery Rule: {rule}")
            return
        for p in rule.network_ranges:
            a = IP.prefix(p.network)
            if a.size == 1:
                yield a
                continue
            for x in a.iter_address(count=a.size):
                yield x

    @classmethod
    def iter_address_scan(cls) -> Iterable[IP]:
        """Iterate over addresses set by IP Scan IPAM flag"""
        from noc.ip.models.prefix import Prefix
        from noc.ip.models.prefix import PrefixProfile

        connect()
        profiles = PrefixProfile.objects.filter(enable_ip_ping_discovery=True)
        if profiles:
            for p in Prefix.objects.filter(profile__in=profiles):
                if "netbox::role::public" in p.labels:
                    continue
                p = IP.prefix(p.prefix)
                if p.size == 1:
                    yield p
                    continue
                for x in p.iter_address(count=p.size):
                    yield x

    @staticmethod
    def parse_credentials(
        community, snmp_user
    ) -> List[Tuple[Protocol, Union[SNMPCredential, SNMPv3Credential]]]:
        """
        Parse SNMP Credentials arguments
        Args:
            community: SNMPv1/v2c community strings, separate by comma
            snmp_user: SNMPv3 credential user: <user>:<auth_proto>:<auth_key>:<priv_proto>:<priv_key>
        """
        r = []
        if community:
            for c in community.split(","):
                r.append(((Protocol(6), Protocol(7)), SNMPCredential(snmp_ro=c, oids=OIDS)))
        if not snmp_user:
            return r
        for c in (snmp_user or "").split(","):
            # user:sha:123456:des:123457
            creds = {"oids": OIDS}
            username, *other = c.split(":")
            creds["username"] = username
            if len(other) >= 2:
                # authNoPriv
                creds.update({"auth_proto": other[0], "auth_key": other[1]})
            if len(other) > 2:
                # authPriv
                creds.update({"private_proto": other[2], "private_key": other[3]})
            r.append((Protocol(8), SNMPv3Credential(**creds)))
        return r

    @staticmethod
    def parse_checks(
        address: str,
        checks: Optional[str] = None,
        ports: Optional[str] = None,
        snmp_cred: Optional[SNMPCredential] = None,
        rule: Optional[Any] = None,
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
            yield Check(name=TCP_CHECK, address=address, port=p)
        if rule:
            for c in rule.checks:
                yield Check(
                    name=c.check,
                    address=address,
                    port=c.port,
                    args={"arg0": c.arg0},
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
                credential=snmp_cred,
            )

    @staticmethod
    def parse_data(data: List[DataItem], params: Dict[str, Any]) -> Dict[str, str]:
        """Parse collected data"""
        r = {}
        if not data:
            return r
        for d in data:
            r[d.name] = d.value
        if HOSTNAME_OID in r:
            params["hostname"] = r[HOSTNAME_OID]
        if DESCR_OID in r:
            params["description"] = r[DESCR_OID]
        if UPTIME_OID in r:
            params["uptime"] = r[UPTIME_OID]
        if CHASSIS_OID in r:
            params["chassis_id"] = r[CHASSIS_OID]
        return r

    def print_out(self, address: str, rtt: float, checks: List[ProtocolCheckResult]):
        """
        Format out result
        """
        # r = []
        # for c in checks:
        #     r.append(f"{c.check}:{c.port} {'OK' if c.status else 'FAIL'}")
        self.stdout.write(
            f"{address} {rtt * 1_000:.2f}ms| {';'.join('%s:%s %s' % (c.check, c.port or '', 'OK' if c.status else 'FAIL') for c in checks)}\n"
        )


if __name__ == "__main__":
    Command().run()
