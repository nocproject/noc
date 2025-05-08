# ----------------------------------------------------------------------
# ./noc inventory command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
from typing import Optional

# NOC modules
from noc.core.inv.codec import decode, encode, InvData
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.inv.models.object import Object


class Command(BaseCommand):
    help = "Query inventory"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # find-serial command
        find_serial_parser = subparsers.add_parser("find-serial")
        find_serial_parser.add_argument(
            "serials", nargs=argparse.REMAINDER, help="Serials to search"
        )
        # export command
        export_parser = subparsers.add_parser("export", help="Export Inventory tree to JSON-file")
        export_parser.add_argument(
            "--output", "-o", help="Destination JSON-file. If not specified - to stdout"
        )
        export_parser.add_argument(
            "objects", nargs=argparse.REMAINDER, help="List of parent objects to export"
        )
        # import command
        import_parser = subparsers.add_parser("import", help="Import Inventory tree from JSON-file")
        import_parser.add_argument("--input", "-i", help="Source JSON-file", required=True)
        import_parser.add_argument(
            "--container",
            "-c",
            dest="container_id",
            help="Container object for importing objects. If not specified - it is root",
        )

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

    def handle_export(self, objects: list[str], output: Optional[str] = None):
        connect()
        inv_data: InvData = encode(Object.objects.filter(id__in=objects))
        json_data = inv_data.model_dump_json(by_alias=True, indent=2)
        if not output:
            self.print(json_data)
        else:
            with open(output, "w") as f:
                f.write(json_data)
        self.print("------------------------------------------")
        self.print("Export finished.")
        self.print(f"Exported Objects: {len(inv_data.objects)}")
        self.print(f"Exported Connections: {len(inv_data.connections)}")
        if output:
            self.print(f"Wrote to file: {output}")

    def handle_import(self, input: str, container_id: Optional[str] = None):
        connect()
        container = Object.get_by_id(container_id)
        if not container:
            self.print(f"Container with ID {container_id} not found")
            return
        with open(input, "r") as f:
            json_data = f.read()
        inv_data = InvData.model_validate_json(json_data)
        result = decode(container, inv_data)
        self.print("result", result, type(result))


if __name__ == "__main__":
    Command().run()
