# ----------------------------------------------------------------------
# ./noc run command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
from threading import Condition

# Third-party modules
from noc.core.threadpool import ThreadPoolExecutor

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.inv.models.resourcegroup import ResourceGroup


class Command(BaseCommand):
    DEFAULT_LIMIT = 20

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        cli_parser = subparsers.add_parser("cli")
        cli_parser.add_argument("--limit", default=self.DEFAULT_LIMIT, help="Concurrency limit")
        cli_parser.add_argument("--command", "-c", action="append", help="Command to execute")
        cli_parser.add_argument(
            "objects", nargs=argparse.REMAINDER, help="Managed objects or expressions"
        )
        #
        # snippet_parser = subparsers.add_parser("snippet")
        # script_parser = subparsers.add_parser("script")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def iter_objects(self, objects):
        r = set()
        connect()
        for x in objects:
            for o in ResourceGroup.get_objects_from_expression(x, model_id="sa.ManagedObject"):
                r.add(o)
        yield from r

    def handle_cli(self, limit, command, objects, *args, **options):
        def run_script(o, script, *args, **kwargs):
            s = getattr(o.scripts, script)
            try:
                result = s(*args, **kwargs)["output"]
            except Exception as e:
                result = f"ERROR: {str(e)}"
            with cond:
                buffer.append((o, result))
                cond.notify()

        if not command:
            return
        cond = Condition()
        buffer = []
        with ThreadPoolExecutor(max_workers=limit) as pool:
            left = 0
            for o in self.iter_objects(objects):
                left += 1
                pool.submit(run_script, o, "commands", commands=command)
            while left > 0:
                with cond:
                    if not buffer:
                        cond.wait()
                    data, buffer = buffer, []
                for o, r in data:
                    self.stdout.write("@@@ %s %s\n%s\n" % (o.address, o.name, "".join(r)))
                    left -= 1


if __name__ == "__main__":
    Command().run()
