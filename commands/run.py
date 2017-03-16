# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc run command
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import argparse
## Third-party modules
from concurrent.futures import ThreadPoolExecutor, as_completed
## NOC modules
from noc.core.management.base import BaseCommand
from noc.sa.models.managedobjectselector import ManagedObjectSelector


class Command(BaseCommand):
    DEFAULT_LIMIT = 100

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        cli_parser = subparsers.add_parser("cli")
        cli_parser.add_argument(
            "--limit",
            default=self.DEFAULT_LIMIT,
            help="Concurrency limit"
        )
        cli_parser.add_argument(
            "--command", "-c",
            action="append",
            help="Command to execute"
        )
        cli_parser.add_argument(
            "objects",
            nargs=argparse.REMAINDER,
            help="Managed objects or expressions"
        )
        #
        # snippet_parser = subparsers.add_parser("snippet")
        # script_parser = subparsers.add_parser("script")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def iter_objects(self, objects):
        r = set()
        for x in objects:
            for o in ManagedObjectSelector.resolve_expression(x):
                r.add(o)
        for o in r:
            yield o

    def run_script(self, object, script, *args, **kwargs):
        s = getattr(object.scripts, script)
        return object, s(*args, **kwargs)

    def handle_cli(self, limit, command, objects, *args, **options):
        if not command:
            return
        with ThreadPoolExecutor(max_workers=limit) as executor:
            futures = []
            for o in self.iter_objects(objects):
                futures += [
                    executor.submit(self.run_script, o,
                                    "commands", commands=command)
                ]
            for future in as_completed(futures):
                try:
                    o, result = future.result()
                    self.stdout.write("@@@ %s %s\n%s\n" % (o.address, o.name, "".join(result)))
                except Exception as e:
                    self.stdout.write("[%s] [%s] ERROR: %s\n" % (o.address, o.name,  e))

if __name__ == "__main__":
    Command().run()
