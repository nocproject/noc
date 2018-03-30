# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Pretty command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
# Third-party modules
from tornado.ioloop import IOLoop
import tornado.gen
import tornado.queues
# NOC modules
from noc.core.management.base import BaseCommand
from noc.lib.validators import is_ipv4
from noc.core.ioloop.snmp import snmp_get, SNMPError
from noc.sa.interfaces.base import MACAddressParameter


class Command(BaseCommand):
    DEFAULT_OID = "1.3.6.1.2.1.1.2.0"
    DEFAULT_COMMUNITY = "public"

    def add_arguments(self, parser):
        parser.add_argument(
            "--in",
            action="append",
            dest="input",
            help="File with addresses"
        )
        parser.add_argument(
            "--jobs",
            action="store",
            type=int,
            default=100,
            dest="jobs",
            help="Concurrent jobs"
        )
        parser.add_argument(
            "--community",
            action="append",
            help="SNMP community"
        )
        parser.add_argument(
            "--oid",
            default=self.DEFAULT_OID,
            help="SNMP GET OID"
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=5,
            help="SNMP GET timeout"
        )
        parser.add_argument(
            "addresses",
            nargs=argparse.REMAINDER,
            help="Object name"
        )
        parser.add_argument(
            "--convert",
            type=bool,
            default=False,
            help="convert mac address"
        )
        parser.add_argument(
            "--version",
            type=int,
            help="version snmp check"
        )

    def handle(self, input, addresses, jobs, community, oid, timeout, convert, version,
               *args, **options):
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
        self.ioloop = IOLoop.current()
        self.jobs = jobs
        self.convert = convert
        self.version = version
        self.queue = tornado.queues.Queue(self.jobs)
        for i in range(self.jobs):
            self.ioloop.spawn_callback(self.poll_worker,
                                       community, oid, timeout, version)
        self.ioloop.run_sync(self.poll_task)

    @tornado.gen.coroutine
    def poll_task(self):
        for a in self.addresses:
            yield self.queue.put(a)
        for i in range(self.jobs):
            yield self.queue.put(None)
        yield self.queue.join()

    @tornado.gen.coroutine
    def poll_worker(self, community, oid, timeout, version):
        while True:
            a = yield self.queue.get()
            if a:
                for c in community:
                    t0 = self.ioloop.time()
                    try:
                        r = yield snmp_get(
                            address=a,
                            oids=oid,
                            community=c,
                            version=version,
                            timeout=timeout
                        )
                        s = "OK"
                        dt = self.ioloop.time() - t0
                        mc = c
                        break
                    except SNMPError as e:
                        s = "FAIL"
                        r = str(e)
                        dt = self.ioloop.time() - t0
                        mc = ""
                    except Exception as e:
                        s = "EXCEPTION"
                        r = str(e)
                        dt = self.ioloop.time() - t0
                        mc = ""
                        break
                if self.convert:
                    try:
                        r = MACAddressParameter().clean(r)
                    except ValueError:
                        pass
                self.stdout.write(
                    "%s,%s,%s,%s,%r\n" % (a, s, dt, mc, r)
                )
            self.queue.task_done()
            if not a:
                break


if __name__ == "__main__":
    Command().run()
