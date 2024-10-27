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
from typing import Tuple, Iterable

# Third-party modules
from gufo.snmp import SnmpSession, SnmpVersion, SnmpError as GSNMPError
from gufo.snmp.user import User, Aes128Key, DesKey, Md5Key, Sha1Key, KeyType

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.validators import is_ipv4
from noc.core.ioloop.util import run_sync
from noc.core.snmp.version import SNMP_v1, SNMP_v2c, SNMP_v3
from noc.sa.interfaces.base import MACAddressParameter

AUTH_PROTO_MAP = {
    "MD5": Md5Key,
    "SHA": Sha1Key,
}

PRIV_PROTO_MAP = {
    "DES": DesKey,
    "AES": Aes128Key,
}


class Command(BaseCommand):
    DEFAULT_OID = "1.3.6.1.2.1.1.2.0"
    DEFAULT_COMMUNITY = "public"
    VERSION_MAP = {"v1": SNMP_v1, "v2c": SNMP_v2c, "v3": SNMP_v3}

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
        getnext = subparsers.add_parser("getnext")
        getnext.add_argument("--community", help="SNMP community")
        getnext.add_argument(
            "--username",
            help="SNMPv3 credentials: <user>:<auth_proto>:<auth_key>:<priv_proto>:<prive_key>",
        )
        getnext.add_argument("--address", help="Object address")
        getnext.add_argument("--timeout", type=int, default=5, help="SNMP GET timeout")
        getnext.add_argument("oid", nargs=argparse.REMAINDER, help="SNMP GET OID")
        getbulk = subparsers.add_parser("getbulk")
        getbulk.add_argument("--community", help="SNMP community")
        getbulk.add_argument(
            "--username",
            help="SNMPv3 credentials: <user>:<auth_proto>:<auth_key>:<priv_proto>:<prive_key>",
        )
        getbulk.add_argument("--address", help="Object address")
        getbulk.add_argument("--timeout", type=int, default=5, help="SNMP GETBULK timeout")
        getbulk.add_argument("oid", nargs=argparse.REMAINDER, help="SNMP GETBULK OID")
        poll = subparsers.add_parser("poll")
        poll.add_argument("--in", action="append", dest="input", help="File with addresses")
        poll.add_argument(
            "--jobs", action="store", type=int, default=100, dest="jobs", help="Concurrent jobs"
        )
        poll.add_argument("--community", action="append", help="SNMP community")
        poll.add_argument(
            "--username",
            action="append",
            help="SNMPv3 credentials: <user>:<auth_proto>:<auth_key>:<priv_proto>:<prive_key>",
        )
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

    @staticmethod
    def parse_credentials(snmp_user: str):
        user, *creds = snmp_user.split(":")
        auth, priv = None, None
        if len(creds) >= 2:
            auth = AUTH_PROTO_MAP[creds[0]](creds[1].encode(), key_type=KeyType.Password)
        if len(creds) > 2:
            priv = PRIV_PROTO_MAP[creds[2]](creds[3].encode(), key_type=KeyType.Password)
        return User(name=str(user), auth_key=auth, priv_key=priv)

    def handle_get(self, address, community, timeout, oids, username, *args, **options):
        """ """

        async def main():
            async with SnmpSession(
                addr=address,
                community=community,
                user=username,
                timeout=timeout,
                version=SnmpVersion.v3 if username else SnmpVersion.v2c,
            ) as session:
                r = await session.get_many(oids)
            return r

        if username:
            username = self.parse_credentials(username)
        x = run_sync(main)
        self.print(f"Result {x}")

    def handle_getnext(self, address, community, timeout, oid, username, *args, **options):
        """ """

        async def main():
            r = []
            async with SnmpSession(
                addr=address,
                community=community,
                user=username,
                timeout=timeout,
                version=SnmpVersion.v3 if username else SnmpVersion.v2c,
            ) as session:
                async for oid_, v in session.getnext(oid[0]):
                    r.append((oid_, v))
            return r

        if username:
            username = self.parse_credentials(username)
        x = run_sync(main)
        self.print(f"Result {x}")

    def handle_getbulk(self, address, community, timeout, oid, username, *args, **options):
        """ """

        async def main():
            r = []
            async with SnmpSession(
                addr=address,
                community=community,
                user=username,
                timeout=timeout,
                version=SnmpVersion.v3 if username else SnmpVersion.v2c,
            ) as session:
                async for oid_, v in session.getbulk(oid[0]):
                    r.append((oid_, v))
            return r

        if username:
            username = self.parse_credentials(username)
        x = run_sync(main)
        self.print(f"Result {x}")

    def handle_poll(
        self,
        input,
        addresses,
        jobs,
        community,
        username,
        oid,
        timeout,
        convert,
        version,
        *args,
        **options,
    ):
        async def main():
            loop = asyncio.get_running_loop()
            # Schedule workers
            queue = asyncio.Queue()
            for _ in range(self.jobs):
                loop.create_task(
                    self.poll_worker(
                        queue, community, username, oid, timeout, self.version, f"worker-{_}"
                    )
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

    @classmethod
    def iter_credentials(
        cls, community, username, version
    ) -> Iterable[Tuple[str, User, SnmpVersion]]:
        if version != SNMP_v3:
            for c in community:
                yield c, None, SnmpVersion.v2c if not version else SnmpVersion.v1
            return
        for user in username:
            user = cls.parse_credentials(user)
            yield None, user, SnmpVersion.v3

    async def poll_worker(self, queue, community, username, oid, timeout, version, name):
        while True:
            a = await queue.get()
            if a:
                for c, user, v in self.iter_credentials(community, username, version):
                        session = SnmpSession(
                            addr=a,
                            community=c,
                            user=user,
                            timeout=timeout,
                            version=v,
                            engine_id=bytes.fromhex("80003a8c04"),
                            t0=perf_counter()
                        )
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
