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

    PB_LENGTH = 80

    def printbox(self, line: str):
        self.print(f"| {line.ljust(self.PB_LENGTH)} |")

    def printbox_border(self):
        self.print("=" * (self.PB_LENGTH + 4))

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
        inv_data, result_info = encode(Object.objects.filter(id__in=objects))
        json_data = inv_data.model_dump_json(by_alias=True, indent=2)
        if output:
            with open(output, "w") as f:
                f.write(json_data)
        else:
            self.print(json_data)
        self.printbox_border()
        if output:
            self.printbox(f"Export to file: '{output}'")
        else:
            self.printbox("Export to stdout")
        self.printbox("-" * self.PB_LENGTH)
        self.printbox("")
        self.printbox("Found")
        self.printbox(f"  - objects: {result_info.found_objects}")
        self.printbox(f"  - direct connections: {result_info.found_connections_direct}")
        self.printbox(f"  - cable connections: {result_info.found_connections_cable}")
        self.printbox_border()

    def handle_import(self, input: str, container_id: Optional[str] = None):
        connect()
        container = Object.get_by_id(container_id)
        if not container:
            self.print(f"Container with ID {container_id} not found")
            return
        with open(input, "r") as f:
            json_data = f.read()
        inv_data = InvData.model_validate_json(json_data)
        result, result_info = decode(container, inv_data)
        self.printbox_border()
        self.printbox(f"Import from file: '{input}'")
        self.printbox("-" * self.PB_LENGTH)
        self.printbox("")
        self.printbox("Found")
        self.printbox(f"  - objects: {result_info.found_objects}")
        self.printbox(f"  - direct connections: {result_info.found_connections_direct}")
        self.printbox(f"  - cable connections: {result_info.found_connections_cable}")
        self.printbox("Created")
        self.printbox(f"  - objects: {result_info.created_objects}")
        self.printbox(f"  - direct connections: {result_info.created_connections_direct}")
        self.printbox(f"  - cable model: {result_info.created_cable_model}")
        self.printbox(f"  - cables: {result_info.created_cable}")
        self.printbox(f"  - cable connections: {result_info.created_connections_cable}")
        self.printbox_border()


if __name__ == "__main__":
    Command().run()
