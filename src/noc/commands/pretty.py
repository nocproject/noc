# ----------------------------------------------------------------------
#  Pretty command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import json
import sys
import pprint
import argparse

# Third-party modules
import yaml

# NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--yaml", action="store_const", dest="format", const="yaml", help="YAML output"
        )
        parser.add_argument(
            "--json", action="store_const", dest="format", const="json", help="JSON output"
        )

    def handle(self, format, *args, **options):
        # Load file
        data = json.load(sys.stdin)
        format = format or "json"
        if format == "json":
            pprint.pprint(data)
        elif format == "yaml":
            yaml.dump(data, sys.stdout)
