# ----------------------------------------------------------------------
# set-slots command
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
        print("!")
        parser.add_argument(
            "-f", "--file", nargs=argparse.REMAINDER, help="Read arguments from file"
        )

    def handle(self, *args, **options):
        async def inner() -> None:
            for k, v in sorted(limits):
                await dcs.set_slot_limit(k, v)

        limits: Dict[str, int] = {}
        files = options.get("file")
        if files:
            for fn in files:
                with open(fn) as fp:
                    for line in fp:
                        k, v = line.strip().split()
                        limits[k] = int(v)
        dcs = get_dcs()
        asyncio.run(inner())


if __name__ == "__main__":
    Command().run()
