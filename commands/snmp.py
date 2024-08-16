# ----------------------------------------------------------------------
# Pretty command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import asyncio
from time import perf_counter

# Third-party modules
from gufo.snmp import SnmpSession, SnmpVersion, SnmpError as GSNMPError
from gufo.snmp.user import User, Aes128Key, DesKey, Md5Key, Sha1Key, KeyType

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.validators import is_ipv4
from noc.core.ioloop.util import run_sync
from noc.core.snmp.version import SNMP_v1, SNMP_v2c
from noc.sa.interfaces.base import MACAddressParameter


class Command(BaseCommand):
    DEFAULT_OID = "1.3.6.1.2.1.1.2.0"
    DEFAULT_COMMUNITY = "public"
    VERSION_MAP = {"v1": SNMP_v1, "v2c": SNMP_v2c}

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        get = subparsers.add_parser("get")
        get.add_argument("--community", help="SNMP community")
        get.add_argument(
            "--username",
            help="SNMPv3 credentials: <user>:<auth_proto>:<auth_key>:<priv_proto>:<prive_key>",
        )
        get.add_argument("--address", help="Object address")
        get.add_argument("--timeout", type=int, default=5, help="SNMP GET timeout")
        get.add_argument("oids", nargs=argparse.REMAINDER, help="SNMP GET OID")
        poll = subparsers.add_parser("poll")
        poll.add_argument("--in", action="append", dest="input", help="File with addresses")
        poll.add_argument(
            "--jobs", action="store", type=int, default=100, dest="jobs", help="Concurrent jobs"
        )
        poll.add_argument("--community", action="append", help="SNMP community")
        poll.add_argument("--oid", default=self.DEFAULT_OID, help="SNMP GET OID")
        poll.add_argument("--timeout", type=int, default=5, help="SNMP GET timeout")
        poll.add_argument("addresses", nargs=argparse.REMAINDER, help="Object name")
        poll.add_argument("--convert", type=bool, default=False, help="convert mac address")
        poll.add_argument(
            "--version",
            type=str,
            default="v2c",
            choices=list(sorted(self.VERSION_MAP)),
            help="version snmp check",
        )

    def handle(self, *args, **options):
        cmd = options["cmd"]
        return getattr(self, f'handle_{cmd.replace("-", "_")}')(*args, **options)

    def handle_get(self, address, community, timeout, oids, *args, **options):
        """ """

        async def main():
            session = SnmpSession(
                addr=address, community=community, timeout=timeout,  # version=version,
            )
            r = await session.get(oids)
            return r

        x = run_sync(main)
        self.print(f"Result {x}")

    def handle_poll(
        self, input, addresses, jobs, community, oid, timeout, convert, version, *args, **options
    ):
        async def main():
            loop = asyncio.get_running_loop()
            # Schedule workers
            queue = asyncio.Queue()
            for _ in range(self.jobs):
                loop.create_task(
                    self.poll_worker(queue, community, oid, timeout, self.version, f"worker-{_}")
                )
            await self.poll_task(queue)

        self.addresses = set()
        # Direct addresses
        for a in addresses:
            if is_ipv4(a):
                self.addresses.add(a)
        # Read addresses from files
        if input:
            for fn in input:
                try:
                    with open(fn) as f:
                        for line in f:
                            line = line.strip()
                            if is_ipv4(line):
                                self.addresses.add(line)
                except OSError as e:
                    self.die("Cannot read file %s: %s\n" % (fn, e))
        # @todo: Add community oid check
        if not community:
            community = [self.DEFAULT_COMMUNITY]
        # Ping
        self.jobs = jobs
        self.convert = convert
        self.version = self.VERSION_MAP[version]
        asyncio.run(main())

    async def poll_task(self, queue):
        for a in self.addresses:
            await queue.put(a)
        for i in range(self.jobs):
            await queue.put(None)
        await queue.join()

    async def poll_worker(self, queue, community, oid, timeout, version, name):
        while True:
            a = await queue.get()
            if a:
                for c in community:
                    session = SnmpSession(addr=a, community=c, timeout=timeout, version=version)
                    t0 = perf_counter()
                    try:
                        r = await session.get(oid)
                        s = "OK"
                        dt = perf_counter() - t0
                        mc = c
                        break
                    except (TimeoutError, GSNMPError) as e:
                        s = "FAIL"
                        r = str(e)
                        dt = perf_counter() - t0
                        mc = ""
                    except Exception as e:
                        s = "EXCEPTION"
                        r = str(e)
                        dt = perf_counter() - t0
                        mc = ""
                        break
                if self.convert:
                    try:
                        r = MACAddressParameter().clean(r)
                    except ValueError:
                        pass
                self.stdout.write(f"[{name}] {a},{s},{dt},{mc},{r!r}\n")
            queue.task_done()
            if not a:
                break


if __name__ == "__main__":
    Command().run()
