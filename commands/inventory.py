# ----------------------------------------------------------------------
# ./noc inventory command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.inv.models.object import Object


class Command(BaseCommand):
    help = "Query inventory"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        #
        rebuild_parser = subparsers.add_parser("find-serial")
        rebuild_parser.add_argument("serials", nargs=argparse.REMAINDER, help="Serials to search")

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_find_serial(self, serials):
        connect()
        for serial in serials:
            for obj in Object.objects.filter(
                data__match={"interface": "asset", "attr": "serial", "value": serial}
            ):
                self.print("@@@ Serial %s" % serial)
                self.dump_object(obj)

    def dump_object(self, obj):
        def obj_str(o, conn_name=None):
            r = []
            if conn_name:
                r += ["%s:" % conn_name]
            if o.name:
                r += [str(o.name)]
            r += ["(%s)" % o.model.name]
            sn = o.get_data("asset", "serial")
            if sn:
                r += ["Serial=%s" % sn]
            return " ".join(r)

        def iter_obj(o):
            if o.parent and o.parent_connection:
                # Allow follow up
                yield obj_str(o, o.parent_connection)
                # Follow up
                yield from iter_obj(o.parent)
            else:
                # Try up to container
                yield obj_str(o)
                if o.parent:
                    yield from iter_obj(o.parent)

        for n, sr in enumerate(reversed(list(iter_obj(obj)))):
            self.print("%s * %s" % ("  " * n, sr))


if __name__ == "__main__":
    Command().run()
