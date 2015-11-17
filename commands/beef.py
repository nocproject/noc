# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Beef management
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import pprint
import glob
import os
## NOC modules
from noc.core.management.base import BaseCommand
from noc.core.script.beef import Beef


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # view command
        view_parser = subparsers.add_parser("view")
        view_parser.add_argument(
            "beef",
            nargs=1,
            help="Beef UUID or path"
        )
        # list command
        list_parser = subparsers.add_parser("list")
        # test command
        test_parser = subparsers.add_parser("test")
        test_parser.add_argument(
            "beef",
            nargs=1,
            help="Beef UUID or path"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_view(self, beef, *args, **options):
        b = Beef.load_by_id(beef[0])
        if not b:
            self.die("Beef not found: %s" % beef[0])
        r = [
            "===[ %s {%s} ]==========" % (b.script, b.guid),
            "Platform : %s %s" % (b.vendor, b.platform),
            "Version  : %s" % b.version,
            "Date     : %s" % b.date
        ]
        if b.input:
            r += ["---[ Input ]-----------"]
            r += [pprint.pformat(b.input), ""]
        if b.result:
            if (isinstance(b.result, basestring) and
                    "START OF TRACEBACK" in b.result):
                r += [
                    "---[ Traceback ]-----------",
                    b.result,
                ]
            else:
                r += [
                    "---[ Result ]-----------",
                    pprint.pformat(b.result),
                ]
        # Dump CLI commands
        if b.cli:
            r += [
                "---[ CLI ]-----------"
            ]
            for cmd in b.cli:
                r += [
                    "-----> %s" % cmd,
                    b.cli[cmd],
                ]
        # DUMP SNMP GET
        if b.snmp_get:
            r += [
                "---[SNMP GET]---",
                pprint.pformat(b.snmp_get),
            ]
        if b.snmp_getnext:
            r += [
                "---[SNMP GETNEXT]---",
                pprint.pformat(b.snmp_getnext),
            ]
        # Dump output
        self.stdout.write("\n".join(r) + "\n")
        return

    def handle_list(self, *options, **args):
        r = ["Provider,Profile,Script,Vendor,Platform,Version,UUID"]
        for path in glob.glob(
            os.path.join(Beef.BEEF_ROOT, "*/*/*/*/*.json")
        ):
            parts = path.split(os.sep)
            provider = parts[3]
            b = Beef()
            b.load(path)
            profile, script = b.script.rsplit(".", 1)
            r += ["%s,%s,%s,%s,%s,%s,%s" % (
                provider, profile, script,
                b.vendor, b.platform, b.version, b.guid)]
        # Dump output
        self.stdout.write("\n".join(r) + "\n")
        return

    def handle_test(self, beef, *options, **args):
        from noc.core.script.loader import loader

        b = Beef.load_by_id(beef[0])
        if not b:
            self.die("Beef not found: %s" % beef[0])
        script_class = loader.get_script(b.script)
        if not script_class:
            self.die("Invalid script: %s", b.script)
        # Build credentials
        credentials = {
            "address": b.guid,
            "cli_protocol": "beef",
            "beef": b
        }
        # Get capabilities
        caps = {}
        # Run script
        service = ServiceStub(pool="default")
        scr = script_class(
            service=service,
            credentials=credentials,
            capabilities=caps,
            version={
                "vendor": b.vendor,
                "platform": b.platform,
                "version": b.version
            },
            timeout=3600,
            name=b.script
        )
        result = scr.run()
        pprint.pprint(result)


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)

if __name__ == "__main__":
    Command().run()
