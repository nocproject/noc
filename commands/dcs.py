# ----------------------------------------------------------------------
# dcs command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
from typing import Dict
import asyncio

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.service.loader import get_dcs


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        set_slots = subparsers.add_parser("set-slots")
        set_slots.add_argument(
            "-f", "--file", nargs=argparse.REMAINDER, help="Read arguments from file"
        )

    def handle(self, *args, **options):
        cmd = options["cmd"]
        return getattr(self, f'handle_{cmd.replace("-", "_")}')(*args, **options)

    def handle_set_slots(self, *args, **options):
        async def inner() -> None:
            for k, v in sorted(limits.items()):
                await dcs.set_slot_limit(k, v)

        limits: Dict[str, int] = {}
        files = options.get("file")
        if files:
            for fn in files:
                if fn == "-":
                    fn = "/dev/stdin"
                with open(fn) as fp:
                    for line in fp:
                        k, v = line.split(":")
                        limits[k.strip()] = int(v.strip())
        dcs = get_dcs()
        asyncio.run(inner())


if __name__ == "__main__":
    Command().run()
